"""FastAPI server for sber-tunnel."""
import os
import signal
import threading
import time
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from ..core.config import Config
from ..db.schema import Database
from ..services.confluence import ConfluenceService
from ..services.sync import SyncService
from ..services.watcher import FileWatcher


# Pydantic models
class DirectoryInfo(BaseModel):
    id: int
    local_path: str
    page_id: str
    last_sync_at: Optional[float] = None


class AddDirectoryRequest(BaseModel):
    local_path: str
    page_id: str


class ImportManifestRequest(BaseModel):
    page_id: str
    local_path: str


class CheckManifestRequest(BaseModel):
    page_id: str


class ManifestInfo(BaseModel):
    exists: bool
    file_count: int
    files: List[dict] = []


class SyncResponse(BaseModel):
    success: bool
    message: str


# Global state
app = FastAPI(title="Sber-tunnel", version="1.0.0")
server_thread = None
watcher_instance = None


def get_config():
    """Get configuration instance."""
    return Config()


def get_confluence():
    """Get Confluence service instance."""
    config = get_config()
    return ConfluenceService(
        url=config.get('base_url'),
        username=config.get('username'),
        password=config.get('password'),
        cert_path=config.get('cert_path'),
        cert_password=config.get('cert_password')
    )


def get_db():
    """Get database instance."""
    config = get_config()
    db_path = config.get_db_path()
    return Database(db_path)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve main UI page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sber-tunnel</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
            }
            .container {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .directory {
                border: 1px solid #ddd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 4px;
            }
            .directory h3 {
                margin-top: 0;
            }
            .info {
                color: #666;
                font-size: 14px;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button.danger {
                background-color: #dc3545;
            }
            button.danger:hover {
                background-color: #c82333;
            }
            input {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                width: 300px;
            }
            .status {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .status.synced {
                background-color: #28a745;
                color: white;
            }
            .status.pending {
                background-color: #ffc107;
                color: black;
            }
        </style>
    </head>
    <body>
        <h1>Sber-tunnel File Synchronization</h1>

        <div class="container">
            <h2>Connect to Confluence Page</h2>
            <input type="text" id="pageId" placeholder="Page ID">
            <button onclick="checkManifest()">Check Page</button>
            <div id="manifestInfo" style="margin-top: 15px;"></div>
        </div>

        <div class="container" id="setupContainer" style="display: none;">
            <h2>Setup Directory</h2>
            <div id="manifestFiles" style="margin-bottom: 15px;"></div>
            <input type="text" id="localPath" placeholder="/path/to/local/directory">
            <button onclick="setupDirectory()">Setup & Sync</button>
        </div>

        <div class="container">
            <h2>Tracked Directories</h2>
            <button onclick="loadDirectories()">Refresh</button>
            <button onclick="syncAll()">Sync All</button>
            <div id="directoriesList"></div>
        </div>

        <script>
            let currentPageId = '';
            let manifestData = null;

            async function checkManifest() {
                const pageId = document.getElementById('pageId').value;
                if (!pageId) {
                    alert('Please enter a Page ID');
                    return;
                }

                currentPageId = pageId;

                const response = await fetch('/api/check-manifest', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({page_id: pageId})
                });

                if (response.ok) {
                    manifestData = await response.json();
                    const infoDiv = document.getElementById('manifestInfo');
                    const filesDiv = document.getElementById('manifestFiles');
                    const setupContainer = document.getElementById('setupContainer');

                    if (manifestData.exists) {
                        infoDiv.innerHTML = `<p style="color: green;">Found ${manifestData.file_count} files on Confluence page.</p>`;

                        let filesHtml = '<p><strong>Files to download:</strong></p><ul>';
                        manifestData.files.forEach(f => {
                            const sizeKB = (f.size / 1024).toFixed(2);
                            filesHtml += `<li>${f.path} (${sizeKB} KB)</li>`;
                        });
                        filesHtml += '</ul>';
                        filesDiv.innerHTML = filesHtml;
                    } else {
                        infoDiv.innerHTML = '<p style="color: orange;">No files found on this page. You can upload a local directory.</p>';
                        filesDiv.innerHTML = '<p>Select a local directory to upload to Confluence:</p>';
                    }

                    setupContainer.style.display = 'block';
                } else {
                    alert('Error checking manifest');
                }
            }

            async function setupDirectory() {
                const localPath = document.getElementById('localPath').value;
                if (!localPath || !currentPageId) {
                    alert('Please enter a local directory path');
                    return;
                }

                const response = await fetch('/api/directories', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        local_path: localPath,
                        page_id: currentPageId
                    })
                });

                if (response.ok) {
                    const dir = await response.json();
                    alert('Directory added. Starting sync...');

                    await syncDirectory(dir.id);

                    document.getElementById('pageId').value = '';
                    document.getElementById('localPath').value = '';
                    document.getElementById('setupContainer').style.display = 'none';
                    document.getElementById('manifestInfo').innerHTML = '';
                    loadDirectories();
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.detail);
                }
            }

            async function loadDirectories() {
                const response = await fetch('/api/directories');
                const dirs = await response.json();

                const list = document.getElementById('directoriesList');
                list.innerHTML = '';

                if (dirs.length === 0) {
                    list.innerHTML = '<p>No directories being tracked.</p>';
                    return;
                }

                dirs.forEach(dir => {
                    const dirDiv = document.createElement('div');
                    dirDiv.className = 'directory';

                    const lastSync = dir.last_sync_at
                        ? new Date(dir.last_sync_at * 1000).toLocaleString()
                        : 'Never';

                    dirDiv.innerHTML = `
                        <h3>${dir.local_path}</h3>
                        <div class="info">
                            <strong>ID:</strong> ${dir.id}<br>
                            <strong>Page ID:</strong> ${dir.page_id}<br>
                            <strong>Last Sync:</strong> ${lastSync}
                        </div>
                        <br>
                        <button onclick="syncDirectory(${dir.id})">Sync Now</button>
                    `;

                    list.appendChild(dirDiv);
                });
            }

            async function syncDirectory(dirId) {
                const response = await fetch(`/api/directories/${dirId}/sync`, {
                    method: 'POST'
                });

                const result = await response.json();
                alert(result.message);
                loadDirectories();
            }

            async function syncAll() {
                const response = await fetch('/api/sync', {method: 'POST'});
                const result = await response.json();
                alert(result.message);
                loadDirectories();
            }

            // Load directories on page load
            loadDirectories();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/directories", response_model=List[DirectoryInfo])
async def get_directories():
    """Get list of tracked directories."""
    with get_db() as db:
        dirs = db.get_all_dirs()
        return [DirectoryInfo(**d) for d in dirs]


@app.post("/api/check-manifest", response_model=ManifestInfo)
async def check_manifest(request: CheckManifestRequest):
    """Check if manifest exists on Confluence page."""
    confluence = get_confluence()
    manifest = confluence.download_manifest(request.page_id)

    if manifest and manifest.files:
        files_list = []
        for f in manifest.files:
            if not f.deleted:
                files_list.append({
                    'path': f.path,
                    'size': f.size,
                    'mtime': f.mtime,
                    'version': f.version
                })
        return ManifestInfo(
            exists=True,
            file_count=len(files_list),
            files=files_list
        )
    else:
        return ManifestInfo(exists=False, file_count=0, files=[])


@app.post("/api/directories", response_model=DirectoryInfo)
async def add_directory(request: AddDirectoryRequest):
    """Add new directory to track."""
    path = Path(request.local_path)

    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")

    with get_db() as db:
        dir_id = db.add_dir(str(path), request.page_id)

        if not dir_id:
            raise HTTPException(status_code=400, detail="Failed to add directory (may already exist)")

        # Start watching this directory
        global watcher_instance
        if watcher_instance:
            watcher_instance.start_watching(str(path))

        return DirectoryInfo(
            id=dir_id,
            local_path=str(path),
            page_id=request.page_id,
            last_sync_at=None
        )


@app.post("/api/directories/{dir_id}/sync", response_model=SyncResponse)
async def sync_directory(dir_id: int, background_tasks: BackgroundTasks):
    """Manually trigger sync for a directory."""
    with get_db() as db:
        dir_info = db.get_dir(dir_id)

        if not dir_info:
            raise HTTPException(status_code=404, detail="Directory not found")

    # Run sync in background
    def do_sync():
        confluence = get_confluence()
        with get_db() as db:
            sync_service = SyncService(confluence, db)
            sync_service.sync_directory(
                dir_id=dir_id,
                local_path=Path(dir_info['local_path']),
                page_id=dir_info['page_id']
            )

    background_tasks.add_task(do_sync)

    return SyncResponse(
        success=True,
        message=f"Sync started for {dir_info['local_path']}"
    )


@app.post("/api/sync", response_model=SyncResponse)
async def sync_all(background_tasks: BackgroundTasks):
    """Manually trigger sync for all directories."""
    def do_sync():
        confluence = get_confluence()
        with get_db() as db:
            dirs = db.get_all_dirs()
            sync_service = SyncService(confluence, db)

            for dir_info in dirs:
                sync_service.sync_directory(
                    dir_id=dir_info['id'],
                    local_path=Path(dir_info['local_path']),
                    page_id=dir_info['page_id']
                )

    background_tasks.add_task(do_sync)

    return SyncResponse(
        success=True,
        message="Sync started for all directories"
    )


@app.post("/api/import-manifest", response_model=DirectoryInfo)
async def import_manifest(request: ImportManifestRequest, background_tasks: BackgroundTasks):
    """Import manifest from Confluence and set local path."""
    local_path = Path(request.local_path)

    if not local_path.exists():
        local_path.mkdir(parents=True, exist_ok=True)

    if not local_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")

    confluence = get_confluence()
    manifest = confluence.download_manifest(request.page_id)

    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found on Confluence")

    with get_db() as db:
        dir_id = db.add_dir(str(local_path), request.page_id)

        if not dir_id:
            raise HTTPException(status_code=400, detail="Failed to add directory (may already exist)")

        global watcher_instance
        if watcher_instance:
            watcher_instance.start_watching(str(local_path))

    def do_sync():
        with get_db() as db:
            sync_service = SyncService(confluence, db)
            sync_service.sync_directory(
                dir_id=dir_id,
                local_path=local_path,
                page_id=request.page_id
            )

    background_tasks.add_task(do_sync)

    return DirectoryInfo(
        id=dir_id,
        local_path=str(local_path),
        page_id=request.page_id,
        last_sync_at=None
    )


def start_server(daemon: bool = False, host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server.

    Args:
        daemon: Run as daemon
        host: Host to bind to
        port: Port to bind to
    """
    global server_thread, watcher_instance

    # Initialize file watcher
    config = get_config()
    db_path = config.get_db_path()
    with Database(db_path) as db:
        watcher_instance = FileWatcher(db)

        # Start watching all tracked directories
        dirs = db.get_all_dirs()
        for dir_info in dirs:
            watcher_instance.start_watching(dir_info['local_path'])

    if daemon:
        # Run in background thread
        def run():
            uvicorn.run(app, host=host, port=port, log_level="info")

        server_thread = threading.Thread(target=run, daemon=True)
        server_thread.start()
        print(f"Server started at http://{host}:{port}")
    else:
        # Run in foreground
        print(f"Starting server at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")


def stop_server():
    """Stop the FastAPI server."""
    global watcher_instance

    if watcher_instance:
        watcher_instance.stop_all()
        watcher_instance = None

    # Send SIGTERM to current process
    os.kill(os.getpid(), signal.SIGTERM)
