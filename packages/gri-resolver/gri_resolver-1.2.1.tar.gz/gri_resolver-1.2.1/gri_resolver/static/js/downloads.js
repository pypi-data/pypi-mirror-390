// Downloads Management for GRI Resolver Web Interface

// Download task variables
let currentTaskId = null;
let taskCheckInterval = null;
let pendingDownloadRequest = null;

// Load regions on page load
async function loadRegions() {
    try {
        const response = await fetch(`${API_BASE}/regions`);
        const data = await response.json();
        const select = document.getElementById('regionSelect');
        if (select) {
            select.innerHTML = '<option value="">Select a region</option>';
            for (const [key, region] of Object.entries(data.regions)) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${region.name} (${key})`;
                select.appendChild(option);
            }
        }
    } catch (error) {
        console.error('Failed to load regions:', error);
    }
}

// Format bytes to human-readable string
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Identify tiles before downloading
async function identifyTiles() {
    // Determine which tab is currently active
    const tilesTab = document.getElementById('tiles');
    const roiTab = document.getElementById('roi');
    const regionTab = document.getElementById('region');
    
    const isTilesActive = tilesTab && tilesTab.classList.contains('active');
    const isROIActive = roiTab && roiTab.classList.contains('active');
    const isRegionActive = regionTab && regionTab.classList.contains('active');
    
    const request = {};
    const limit = document.getElementById('limitInput').value || null;
    
    // Use only the data from the active tab
    if (isTilesActive) {
        // Use tiles from the "By Tiles" tab
        const tilesInput = document.getElementById('tilesInput').value.trim();
        if (tilesInput && tilesInput.trim()) {
            const tileList = tilesInput.split(/\s+/).filter(t => t.trim());
            if (tileList.length > 0) {
                request.tiles = tileList;
            }
        }
        if (!request.tiles) {
            alert('Please enter tile codes in the "By Tiles" tab');
            return;
        }
    } else if (isROIActive) {
        // Use ROI from the "By ROI" tab
        const minLon = document.getElementById('minLon').value;
        const minLat = document.getElementById('minLat').value;
        const maxLon = document.getElementById('maxLon').value;
        const maxLat = document.getElementById('maxLat').value;
        
        if (minLon && minLat && maxLon && maxLat) {
            const minLonVal = parseFloat(minLon);
            const minLatVal = parseFloat(minLat);
            const maxLonVal = parseFloat(maxLon);
            const maxLatVal = parseFloat(maxLat);
            
            // Validate that all values are valid numbers
            if (!isNaN(minLonVal) && !isNaN(minLatVal) && !isNaN(maxLonVal) && !isNaN(maxLatVal)) {
                request.roi = [minLonVal, minLatVal, maxLonVal, maxLatVal];
            } else {
                alert('Please enter valid coordinates in the "By ROI" tab');
                return;
            }
        } else {
            alert('Please define a ROI using the map or enter coordinates in the "By ROI" tab');
            return;
        }
    } else if (isRegionActive) {
        // Use region from the "By Region" tab
        const region = document.getElementById('regionSelect').value;
        if (region && region.trim()) {
            request.region = region;
        } else {
            alert('Please select a region in the "By Region" tab');
            return;
        }
    } else {
        alert('Please select a tab (By Tiles, By ROI, or By Region)');
        return;
    }
    
    if (limit) request.limit = parseInt(limit);

    // Store request for later download
    pendingDownloadRequest = request;

    const previewDiv = document.getElementById('tilesPreview');
    if (!previewDiv) return;
    
    previewDiv.style.display = 'block';
    previewDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p>Identifying tiles...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/tiles/identify`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(request)
        });
        const data = await response.json();

        // Store tiles data for progress tracking
        // Filter out tiles with no items
        const tilesWithItems = data.tiles.filter(tile => tile.item_count > 0);
        window.identifiedTiles = tilesWithItems;

        // Recalculate totals for filtered tiles
        const filteredTotalTiles = tilesWithItems.length;
        const filteredTotalItems = tilesWithItems.reduce((sum, tile) => sum + tile.item_count, 0);

        // Display tiles list
        let html = `<div class="card">
            <div class="card-header">
                <h6>Identified Tiles (${filteredTotalTiles} tiles, ${filteredTotalItems} items)</h6>
            </div>
            <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-sm table-striped" id="tilesTable">
                    <thead>
                        <tr>
                            <th>Tile Code</th>
                            <th>Items</th>
                            <th>Status</th>
                            <th>Preview</th>
                        </tr>
                    </thead>
                    <tbody>`;

        tilesWithItems.forEach((tile, index) => {
            html += `<tr id="tile-row-${tile.tile_code}">
                <td><strong>${escapeHtml(tile.tile_code)}</strong></td>
                <td>${tile.item_count}</td>
                <td id="tile-status-${tile.tile_code}"><span class="badge bg-secondary">Pending</span></td>
                <td><small class="text-muted">`;
            if (tile.items && tile.items.length > 0) {
                tile.items.slice(0, 3).forEach(item => {
                    const dt = item.datetime ? new Date(item.datetime).toLocaleDateString() : '';
                    html += `${escapeHtml(item.id.substring(0, 20))}${item.id.length > 20 ? '...' : ''}${dt ? ' (' + dt + ')' : ''}<br>`;
                });
                if (tile.items.length > 3) {
                    html += `... and ${tile.items.length - 3} more`;
                }
            } else {
                html += 'No items';
            }
            html += `</small></td>
            </tr>`;
        });

        html += `</tbody></table>
            </div>
            <div class="card-footer" id="tilesCardFooter">
                <button class="btn btn-success" onclick="confirmDownload()">Start Download</button>
                <button class="btn btn-secondary" onclick="cancelPreview()">Cancel</button>
            </div>
            <div id="tilesProgressContainer" style="display: none; padding: 15px;">
                <h6>Download Progress</h6>
                <div id="tilesOverallProgress"></div>
                <div id="tilesProgressDetails" class="mt-2"></div>
            </div>
        </div>`;

        previewDiv.innerHTML = html;
    } catch (error) {
        console.error('Identification failed:', error);
        previewDiv.innerHTML = `<div class="alert alert-danger">Failed to identify tiles: ${escapeHtml(error.message)}</div>`;
    }
}

// Confirm and start download
async function confirmDownload() {
    if (!pendingDownloadRequest) {
        alert('No pending download request');
        return;
    }

    // Hide action buttons and show progress container
    const footer = document.getElementById('tilesCardFooter');
    if (footer) footer.style.display = 'none';
    const progressContainer = document.getElementById('tilesProgressContainer');
    if (progressContainer) progressContainer.style.display = 'block';

    // Reset progress display
    const downloadProgress = document.getElementById('downloadProgress');
    if (downloadProgress) {
        downloadProgress.style.display = 'none';
        downloadProgress.innerHTML = '';
    }
    currentTaskId = null;
    if (taskCheckInterval) {
        clearInterval(taskCheckInterval);
        taskCheckInterval = null;
    }

    try {
        const response = await fetch(`${API_BASE}/tiles/download`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(pendingDownloadRequest)
        });
        const data = await response.json();
        currentTaskId = data.task_id;
        // Start checking immediately
        checkTaskStatus();
        // Then check every second
        taskCheckInterval = setInterval(checkTaskStatus, 1000);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Download failed: ' + error.message);
        // Restore buttons on error
        if (footer) footer.style.display = 'block';
        if (progressContainer) progressContainer.style.display = 'none';
    }
}

// Cancel preview
function cancelPreview() {
    const previewDiv = document.getElementById('tilesPreview');
    if (previewDiv) {
        previewDiv.style.display = 'none';
    }
    pendingDownloadRequest = null;
}

// Check task status
async function checkTaskStatus() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/tasks/${currentTaskId}`);
        const task = await response.json();
        
        // Update progress in tiles list if available
        const tilesProgressContainer = document.getElementById('tilesProgressContainer');
        const tilesOverallProgress = document.getElementById('tilesOverallProgress');
        const tilesProgressDetails = document.getElementById('tilesProgressDetails');
        
        // Show status and message (without redundant progress bar)
        if (tilesOverallProgress) {
            tilesOverallProgress.innerHTML = `
                <div class="mb-2">
                    <strong>Status:</strong> ${task.status} | <strong>Stage:</strong> ${task.stage || 'N/A'}
                    ${task.message ? `<br><strong>Message:</strong> ${task.message}` : ''}
                    ${task.error ? `<br><strong>Error:</strong> ${task.error}` : ''}
                </div>
            `;
        }

        // Update progress details in tiles list (simplified)
        if (task.details && tilesProgressDetails) {
            const details = task.details;
            let progressHTML = '';
            
            // Only show Item Progress
            if (details.items_found > 0) {
                const itemsProcessed = details.items_downloaded + details.items_failed;
                progressHTML += `
                    <div class="mt-2">
                        <small>Item Progress: ${itemsProcessed} / ${details.items_found}</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-success" role="progressbar" style="width: ${Math.round((itemsProcessed / details.items_found) * 100)}%"></div>
                        </div>
                    </div>
                `;
            }
            
            // Show all active downloads with individual progress bars
            if (task.active_downloads && task.active_downloads.length > 0) {
                // Format file name helper function
                function formatFileName(fileName) {
                    if (!fileName || fileName === "unknown" || fileName === "extracting") {
                        return fileName || "unknown";
                    }
                    // Try to extract tile code and date from item ID like GRI_L1C_T33NTB_20160705T135045...
                    const match = fileName.match(/_T(\d{2}[A-Z][A-Z]{2})_(\d{8})/);
                    if (match) {
                        return `${match[1]} (${match[2]})`;
                    } else {
                        // Fallback: use last part of the ID if it's very long
                        const parts = fileName.split('_');
                        if (parts.length > 3) {
                            return parts.slice(-2).join('_');
                        } else {
                            return fileName;
                        }
                    }
                }

                progressHTML += `<div class="mt-2"><strong>Active Downloads:</strong></div>`;
                task.active_downloads.forEach((fileProgress) => {
                    const filePercent = fileProgress.percent || 0;
                    const fileSize = fileProgress.total ? formatBytes(fileProgress.total) : '?';
                    const downloadedSize = fileProgress.bytes ? formatBytes(fileProgress.bytes) : '0 B';
                    const displayFileName = formatFileName(fileProgress.file);
                    const isFinished = fileProgress.percent >= 100;
                    const barClass = isFinished ? 'bg-success' : 'bg-info progress-bar-striped progress-bar-animated';
                    
                    progressHTML += `
                        <div class="mt-1">
                            <small>${escapeHtml(displayFileName)}: ${downloadedSize} / ${fileSize} (${filePercent}%)</small>
                            <div class="progress" style="height: 18px;">
                                <div class="progress-bar ${barClass}" 
                                     role="progressbar" 
                                     style="width: ${filePercent}%">${filePercent}%</div>
                            </div>
                        </div>
                    `;
                });
            } else if (task.current_file_progress && task.current_file_progress.file) {
                // Fallback to old single file display if active_downloads not available
                const fileProgress = task.current_file_progress;
                const filePercent = fileProgress.percent || 0;
                const fileSize = fileProgress.total ? formatBytes(fileProgress.total) : '?';
                const downloadedSize = fileProgress.bytes ? formatBytes(fileProgress.bytes) : '0 B';
                let displayFileName = fileProgress.file;
                if (fileProgress.file && fileProgress.file !== "unknown" && fileProgress.file !== "extracting") {
                    const match = fileProgress.file.match(/_T(\d{2}[A-Z][A-Z]{2})_(\d{8})/);
                    if (match) {
                        displayFileName = `${match[1]} (${match[2]})`;
                    } else {
                        const parts = fileProgress.file.split('_');
                        if (parts.length > 3) {
                            displayFileName = parts.slice(-2).join('_');
                        }
                    }
                }
                progressHTML += `
                    <div class="mt-2">
                        <small>Current File: ${escapeHtml(displayFileName)} (${downloadedSize} / ${fileSize})</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-info progress-bar-striped progress-bar-animated" 
                                 role="progressbar" 
                                 style="width: ${filePercent}%">${filePercent}%</div>
                        </div>
                    </div>
                `;
            }
            
            tilesProgressDetails.innerHTML = progressHTML;
            
            // Update individual tile status based on task stage and progress
            if (window.identifiedTiles) {
                // Helper function to extract tile code from item_id (format: GRI_L1C_T30TWT_...)
                function extractTileFromItemId(itemId) {
                    if (!itemId) return null;
                    const match = itemId.match(/_T(\d{2}[A-Z][A-Z]{2})/);
                    return match ? match[1] : null;
                }
                
                // Initialize status for all identified tiles (preserve existing status if available)
                const tilesStatus = {};
                const tilesDownloadedCount = {}; // Track how many items downloaded per tile
                window.identifiedTiles.forEach(tile => {
                    // Try to preserve existing status from DOM
                    const existingCell = document.getElementById(`tile-status-${tile.tile_code}`);
                    if (existingCell) {
                        const existingBadge = existingCell.querySelector('.badge');
                        if (existingBadge) {
                            const existingText = existingBadge.textContent.trim();
                            if (existingText === 'Searching...') tilesStatus[tile.tile_code] = 'Searching';
                            else if (existingText === 'Found') tilesStatus[tile.tile_code] = 'Found';
                            else if (existingText === 'Downloading...') tilesStatus[tile.tile_code] = 'Downloading';
                            else if (existingText === 'Completed') tilesStatus[tile.tile_code] = 'Completed';
                            else if (existingText === 'Failed') tilesStatus[tile.tile_code] = 'Failed';
                            else if (existingText === 'No items') tilesStatus[tile.tile_code] = 'No items';
                            else tilesStatus[tile.tile_code] = 'Pending';
                        } else {
                            tilesStatus[tile.tile_code] = 'Pending';
                        }
                    } else {
                        tilesStatus[tile.tile_code] = 'Pending';
                    }
                    tilesDownloadedCount[tile.tile_code] = 0;
                });
                
                // Update based on progress messages (most specific status)
                if (task.progress_messages) {
                    task.progress_messages.forEach(msg => {
                        // Try to extract tile code from message
                        let tileCode = null;
                        
                        // Pattern 1: "tile 30TWT: 5 items" or "searching tile 30TWT..."
                        const tileMatch = msg.match(/tile\s+(\w+)/i);
                        if (tileMatch) {
                            tileCode = tileMatch[1];
                        } else {
                            // Pattern 2: Extract from item_id in messages like "cached GRI_L1C_T30TWT_..." or "downloaded ..."
                            const itemIdMatch = msg.match(/(?:cached|downloaded|failed)\s+([^\s]+)/i);
                            if (itemIdMatch) {
                                tileCode = extractTileFromItemId(itemIdMatch[1]);
                            }
                        }
                        
                        if (tileCode) {
                            if (msg.includes('searching')) {
                                tilesStatus[tileCode] = 'Searching';
                            } else if (msg.includes('items') && !msg.includes('0 items')) {
                                tilesStatus[tileCode] = 'Found';
                            } else if (msg.includes('downloaded') || msg.includes('cached')) {
                                tilesDownloadedCount[tileCode] = (tilesDownloadedCount[tileCode] || 0) + 1;
                                // Check if all items for this tile are downloaded
                                const tileInfo = window.identifiedTiles.find(t => t.tile_code === tileCode);
                                if (tileInfo && tilesDownloadedCount[tileCode] >= tileInfo.item_count) {
                                    tilesStatus[tileCode] = 'Completed';
                                } else {
                                    tilesStatus[tileCode] = 'Downloading';
                                }
                            } else if (msg.includes('failed') || msg.includes('error')) {
                                tilesStatus[tileCode] = 'Failed';
                            } else if (msg.includes('0 items')) {
                                tilesStatus[tileCode] = 'No items';
                            }
                        }
                    });
                }
                
                // Update based on current file being downloaded (most immediate indicator - highest priority)
                if (task.current_file_progress && task.current_file_progress.file && task.current_file_progress.file !== 'unknown') {
                    const currentFile = task.current_file_progress.file;
                    const tileCode = extractTileFromItemId(currentFile);
                    if (tileCode) {
                        // If we're downloading a file for this tile, mark it as Downloading immediately
                        tilesStatus[tileCode] = 'Downloading';
                    }
                }
                
                // Update based on task stage (apply to all tiles)
                if (task.stage === 'resolving') {
                    // During resolving, tiles with items become "Found"
                    window.identifiedTiles.forEach(tile => {
                        if (tilesStatus[tile.tile_code] === 'Pending' || tilesStatus[tile.tile_code] === 'Searching') {
                            // Check if this tile has items found
                            if (task.progress_messages) {
                                const hasFoundMsg = task.progress_messages.some(msg => {
                                    const match = msg.match(/tile\s+(\w+)/i);
                                    return match && match[1] === tile.tile_code && msg.includes('items') && !msg.includes('0 items');
                                });
                                if (hasFoundMsg) {
                                    tilesStatus[tile.tile_code] = 'Found';
                                }
                            }
                        }
                    });
                } else if (task.stage === 'downloading') {
                    // During downloading stage, mark found tiles as "Downloading" if not already completed
                    window.identifiedTiles.forEach(tile => {
                        if (tilesStatus[tile.tile_code] === 'Found') {
                            tilesStatus[tile.tile_code] = 'Downloading';
                        }
                    });
                } else if (task.status === 'completed') {
                    // When completed, mark all non-failed tiles as "Completed"
                    window.identifiedTiles.forEach(tile => {
                        if (tilesStatus[tile.tile_code] !== 'Failed' && tilesStatus[tile.tile_code] !== 'No items') {
                            tilesStatus[tile.tile_code] = 'Completed';
                        }
                    });
                }
                
                // Apply status updates to UI for all tiles
                window.identifiedTiles.forEach(tile => {
                    const statusCell = document.getElementById(`tile-status-${tile.tile_code}`);
                    if (statusCell) {
                        const status = tilesStatus[tile.tile_code] || 'Pending';
                        let badgeClass = 'bg-secondary';
                        let badgeText = 'Pending';
                        
                        if (status === 'Searching') {
                            badgeClass = 'bg-info';
                            badgeText = 'Searching...';
                        } else if (status === 'Found') {
                            badgeClass = 'bg-primary';
                            badgeText = 'Found';
                        } else if (status === 'Downloading') {
                            badgeClass = 'bg-warning';
                            badgeText = 'Downloading...';
                        } else if (status === 'Completed') {
                            badgeClass = 'bg-success';
                            badgeText = 'Completed';
                        } else if (status === 'Failed') {
                            badgeClass = 'bg-danger';
                            badgeText = 'Failed';
                        } else if (status === 'No items') {
                            badgeClass = 'bg-warning';
                            badgeText = 'No items';
                        }
                        
                        statusCell.innerHTML = `<span class="badge ${badgeClass}">${badgeText}</span>`;
                    }
                });
            }
        }
        
        // Show final results in tiles list
        if (task.result && tilesProgressDetails) {
            const result = task.result;
            let resultHTML = '<div class="mt-3"><h6>Results</h6><ul class="list-unstyled">';
            resultHTML += `<li><strong>Downloaded:</strong> ${result.downloaded_items} items</li>`;
            if (result.failed_items > 0) {
                resultHTML += `<li><strong>Failed:</strong> ${result.failed_items} items</li>`;
            }
            if (result.unresolved_tiles && result.unresolved_tiles.length > 0) {
                resultHTML += `<li><strong>Unresolved tiles:</strong> ${result.unresolved_tiles.length}</li>`;
            }
            resultHTML += '</ul></div>';
            tilesProgressDetails.innerHTML += resultHTML;
        }
        
        // Also update legacy progress div if it exists (for backward compatibility)
        const statusDiv = document.getElementById('downloadStatus');
        const progressDiv = document.getElementById('downloadProgress');
        if (progressDiv && !tilesProgressDetails) {
            progressDiv.innerHTML = progressHTML || '';
            // Show final results in legacy div too
            if (task.result) {
                const result = task.result;
                let resultHTML = '<div class="mt-3"><h6>Results</h6><ul class="list-unstyled">';
                resultHTML += `<li><strong>Downloaded:</strong> ${result.downloaded_items} items</li>`;
                if (result.failed_items > 0) {
                    resultHTML += `<li><strong>Failed:</strong> ${result.failed_items} items</li>`;
                }
                if (result.unresolved_tiles && result.unresolved_tiles.length > 0) {
                    resultHTML += `<li><strong>Unresolved tiles:</strong> ${result.unresolved_tiles.length}</li>`;
                }
                resultHTML += '</ul></div>';
                progressDiv.innerHTML += resultHTML;
            }
        }

        if (task.status === 'running') {
            if (!taskCheckInterval) {
                taskCheckInterval = setInterval(checkTaskStatus, 1000); // Check every second for better updates
            }
        } else {
            if (taskCheckInterval) {
                clearInterval(taskCheckInterval);
                taskCheckInterval = null;
            }
            if (task.status === 'completed') {
                // Reload tiles list after a short delay to ensure cache is updated
                setTimeout(() => {
                    if (typeof loadTiles === 'function') {
                        loadTiles();
                    }
                }, 500);
            }
        }
    } catch (error) {
        console.error('Failed to check task status:', error);
    }
}

// Initialize regions on page load
document.addEventListener('DOMContentLoaded', function() {
    loadRegions();
});

