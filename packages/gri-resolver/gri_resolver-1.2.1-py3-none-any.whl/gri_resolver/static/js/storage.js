// Storage Information Management for GRI Resolver Web Interface

// Load storage information
async function loadStorageInfo() {
    try {
        const response = await fetch(`${API_BASE}/storage`);
        const data = await response.json();
        
        const storageDiv = document.getElementById('storageInfo');
        if (!storageDiv) return;
        
        let html = '<div class="row">';
        
        // Cache directory info
        html += `
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Cache Directory</h6>
                        <small class="text-muted">${escapeHtml(data.cache_dir.path)}</small>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <tr>
                                <td><strong>Total Size:</strong></td>
                                <td>${escapeHtml(data.cache_dir.total_size_formatted)}</td>
                            </tr>
                            <tr>
                                <td><strong>File Count:</strong></td>
                                <td>${data.cache_dir.file_count.toLocaleString()}</td>
                            </tr>
                            <tr>
                                <td><strong>Manifest Size:</strong></td>
                                <td>${escapeHtml(data.cache_dir.manifest_size_formatted)}</td>
                            </tr>
                            <tr>
                                <td><strong>Cached Items:</strong></td>
                                <td>${data.total_cached_items.toLocaleString()}</td>
                            </tr>
                            <tr>
                                <td><strong>Total Tiles:</strong></td>
                                <td>${data.total_tiles.toLocaleString()}</td>
                            </tr>
                        </table>
                        ${Object.keys(data.cache_dir.file_types || {}).length > 0 ? `
                            <h6 class="mt-3">File Types</h6>
                            <table class="table table-sm">
                                ${Object.entries(data.cache_dir.file_types).map(([ext, count]) => `
                                    <tr>
                                        <td>${escapeHtml(ext || 'no extension')}</td>
                                        <td>${count.toLocaleString()} files</td>
                                        <td>${data.cache_dir.file_type_sizes[ext] ? escapeHtml(data.cache_dir.file_type_sizes[ext].size_formatted) : 'N/A'}</td>
                                    </tr>
                                `).join('')}
                            </table>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Output directory info
        html += `
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Output Directory</h6>
                        <small class="text-muted">${escapeHtml(data.output_dir.path)}</small>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <tr>
                                <td><strong>Total Size:</strong></td>
                                <td>${escapeHtml(data.output_dir.total_size_formatted)}</td>
                            </tr>
                            <tr>
                                <td><strong>File Count:</strong></td>
                                <td>${data.output_dir.file_count.toLocaleString()}</td>
                            </tr>
                        </table>
                        ${Object.keys(data.output_dir.file_types || {}).length > 0 ? `
                            <h6 class="mt-3">File Types</h6>
                            <table class="table table-sm">
                                ${Object.entries(data.output_dir.file_types).map(([ext, count]) => `
                                    <tr>
                                        <td>${escapeHtml(ext || 'no extension')}</td>
                                        <td>${count.toLocaleString()} files</td>
                                        <td>${data.output_dir.file_type_sizes[ext] ? escapeHtml(data.output_dir.file_type_sizes[ext].size_formatted) : 'N/A'}</td>
                                    </tr>
                                `).join('')}
                            </table>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        html += '</div>';
        
        // Disk usage
        html += `
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Disk Usage</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <strong>Total:</strong> ${escapeHtml(data.disk_usage.total_formatted)}
                                </div>
                                <div class="col-md-3">
                                    <strong>Used:</strong> ${escapeHtml(data.disk_usage.used_formatted)}
                                </div>
                                <div class="col-md-3">
                                    <strong>Free:</strong> ${escapeHtml(data.disk_usage.free_formatted)}
                                </div>
                                <div class="col-md-3">
                                    <strong>Used:</strong> ${data.disk_usage.percent_used}%
                                </div>
                            </div>
                            <div class="progress mt-2" style="height: 25px;">
                                <div class="progress-bar ${data.disk_usage.percent_used > 90 ? 'bg-danger' : data.disk_usage.percent_used > 75 ? 'bg-warning' : 'bg-success'}" 
                                     role="progressbar" 
                                     style="width: ${data.disk_usage.percent_used}%">
                                    ${data.disk_usage.percent_used}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Tile sizes (top 10)
        if (Object.keys(data.tile_sizes || {}).length > 0) {
            html += `
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Storage by Tile (Top 10)</h6>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead>
                                            <tr>
                                                <th>Tile Code</th>
                                                <th>Size</th>
                                                <th>File Count</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${Object.entries(data.tile_sizes).slice(0, 10).map(([tile, info]) => `
                                                <tr>
                                                    <td><strong>${escapeHtml(tile)}</strong></td>
                                                    <td>${escapeHtml(info.size_formatted)}</td>
                                                    <td>${info.file_count}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        storageDiv.innerHTML = html;
    } catch (error) {
        console.error('Failed to load storage info:', error);
        const storageDiv = document.getElementById('storageInfo');
        if (storageDiv) {
            storageDiv.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load storage information: ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}

