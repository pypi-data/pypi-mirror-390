// Tiles Management for GRI Resolver Web Interface

// Get rating stars
function getRatingStars(rating) {
    if (rating === null || rating === undefined) return 'Not rated';
    const ratingNum = parseFloat(rating);
    if (isNaN(ratingNum)) return 'Not rated';
    const fullStars = Math.floor(ratingNum);
    const halfStar = ratingNum % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
}

// Load tiles list
async function loadTiles() {
    try {
        // Clean up missing files first
        const cleanupResponse = await fetch(`${API_BASE}/cache/cleanup`, {
            method: 'POST'
        });
        const cleanupData = await cleanupResponse.json();
        
        // Show cleanup message if items were removed
        if (cleanupData.removed_count > 0) {
            console.log(`Cleaned up ${cleanupData.removed_count} missing cache entries`);
        }
        
        const response = await fetch(`${API_BASE}/tiles`);
        const data = await response.json();
        const tilesList = document.getElementById('tilesList');
        if (!tilesList) return;
        
        if (data.tiles.length === 0) {
            tilesList.innerHTML = '<div class="col-12 text-center"><p>No tiles in cache</p></div>';
            return;
        }

        tilesList.innerHTML = data.tiles.map(tile => {
            const quicklookUrl = tile.top_rated_item_id 
                ? `${API_BASE}/tiles/${tile.tile_code}/images/${tile.top_rated_item_id}?preview=true`
                : null;
            // Escape for JavaScript string: replace ' with \' and " with \"
            const tileCodeEscaped = escapeForJs(tile.tile_code);
            return `
            <div class="col-md-4 mb-3">
                <div class="card tile-card" onclick="showTileDetails('${tileCodeEscaped}')" style="cursor: pointer;">
                    ${quicklookUrl ? `
                        <div class="quicklook-container" style="height: 150px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
                            <div class="quicklook-placeholder" style="position: absolute; color: #999; font-size: 0.8em; text-align: center;">
                                <div class="spinner-border spinner-border-sm" role="status" style="margin-bottom: 5px;">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <div>Loading preview...</div>
                            </div>
                            <img src="" 
                                 data-src="${quicklookUrl}" 
                                 class="card-img-top quicklook-image lazy-quicklook" 
                                 alt="Quicklook ${tile.tile_code}"
                                 style="height: 150px; width: 100%; object-fit: cover; display: none; position: relative; z-index: 1;"
                                 onload="this.style.display='block'; const placeholder = this.parentElement.querySelector('.quicklook-placeholder'); if(placeholder) placeholder.style.display='none';"
                                 onerror="this.style.display='none'; const placeholder = this.parentElement.querySelector('.quicklook-placeholder'); if(placeholder) { placeholder.innerHTML='<div style=\'color: #999;\'>No preview</div>'; }">
                        </div>
                    ` : ''}
                    <div class="card-body">
                        <h6 class="card-title">${tile.tile_code}</h6>
                        <p class="card-text">
                            <small class="text-muted">
                                ${tile.image_count} image(s)<br>
                                Best score: ${tile.best_score !== -Infinity ? tile.best_score.toFixed(2) : 'N/A'}
                                ${tile.top_rated_score !== null && tile.top_rated_score !== undefined ? `<br>Top rated: ${tile.top_rated_score.toFixed(1)}` : ''}
                            </small>
                        </p>
                    </div>
                </div>
            </div>
        `;
        }).join('');
        
        // Load quicklook images lazily using Intersection Observer
        // Use requestAnimationFrame to ensure DOM is updated
        requestAnimationFrame(function() {
            setTimeout(function() {
                const lazyQuicklooks = Array.from(document.querySelectorAll('img.lazy-quicklook[data-src]'));
                
                if (lazyQuicklooks.length === 0) {
                    console.log('No lazy quicklook images found');
                    return;
                }
                
                console.log(`Found ${lazyQuicklooks.length} lazy quicklook images`);
                
                // Function to load an image
                function loadImage(img) {
                    if (!img || !img.nodeName || img.nodeName.toLowerCase() !== 'img') {
                        console.warn('loadImage: invalid image element');
                        return false;
                    }
                    
                    const dataSrc = img.getAttribute('data-src');
                    if (!dataSrc || !dataSrc.trim()) {
                        console.warn('loadImage: no data-src attribute or empty');
                        return false;
                    }
                    
                    // Check if already loaded
                    if (img.src && img.src !== window.location.href && !img.src.endsWith('/')) {
                        console.log('loadImage: image already loaded:', img.src);
                        return false;
                    }
                    
                    try {
                        console.log('loadImage: setting src to:', dataSrc);
                        img.src = dataSrc;
                        img.removeAttribute('data-src');
                        return true;
                    } catch (e) {
                        console.error('loadImage: error setting src:', e);
                        return false;
                    }
                }
                
                // Load all visible images immediately
                const visibleImages = [];
                lazyQuicklooks.forEach(function(img) {
                    const rect = img.getBoundingClientRect();
                    const isVisible = rect.top < window.innerHeight + 200 && rect.bottom > -200;
                    if (isVisible) {
                        visibleImages.push(img);
                        loadImage(img);
                    }
                });
                
                console.log(`Loaded ${visibleImages.length} immediately visible images`);
                
                // Use Intersection Observer for remaining images
                let remainingImages = lazyQuicklooks.filter(function(img) {
                    return img.getAttribute('data-src') !== null;
                });
                
                console.log(`${remainingImages.length} images remaining to load via IntersectionObserver`);
                
                if (remainingImages.length > 0) {
                    // Simple and reliable approach: periodic check that works in all browsers
                    // This avoids issues with event propagation and z-index stacking
                    let periodicCheckInterval;
                    let checkCount = 0;
                    
                    const checkAndLoadVisible = function() {
                        checkCount++;
                        // Re-fetch remaining images (some may have been loaded)
                        const stillRemaining = Array.from(document.querySelectorAll('img.lazy-quicklook[data-src]'));
                        
                        if (stillRemaining.length === 0) {
                            console.log('All images loaded, stopping periodic check');
                            if (periodicCheckInterval) {
                                clearInterval(periodicCheckInterval);
                            }
                            return;
                        }
                        
                        console.log(`Periodic check #${checkCount}: checking ${stillRemaining.length} remaining images`);
                        
                        stillRemaining.forEach(function(img) {
                            try {
                                const rect = img.getBoundingClientRect();
                                // Check if image is visible in viewport (with 300px margin for early loading)
                                const isVisible = rect.top < window.innerHeight + 300 && 
                                                 rect.bottom > -300 &&
                                                 rect.left < window.innerWidth + 300 &&
                                                 rect.right > -300;
                                if (isVisible) {
                                    const dataSrc = img.getAttribute('data-src');
                                    console.log(`Loading visible image: ${dataSrc}`);
                                    if (loadImage(img)) {
                                        console.log(`Successfully loaded: ${dataSrc}`);
                                    }
                                }
                            } catch (e) {
                                console.warn('Error checking image visibility:', e);
                            }
                        });
                    };
                    
                    // Set up IntersectionObserver as primary method
                    let quicklookObserver = null;
                    if ('IntersectionObserver' in window) {
                        try {
                            quicklookObserver = new IntersectionObserver(function(entries, observer) {
                                entries.forEach(function(entry) {
                                    if (entry.isIntersecting) {
                                        const img = entry.target;
                                        const dataSrc = img.getAttribute('data-src');
                                        console.log('IntersectionObserver: loading image:', dataSrc);
                                        if (loadImage(img)) {
                                            observer.unobserve(img);
                                        }
                                    }
                                });
                            }, {
                                root: null,
                                rootMargin: '300px',
                                threshold: 0.01
                            });
                            
                            remainingImages.forEach(function(img) {
                                quicklookObserver.observe(img);
                            });
                            console.log(`IntersectionObserver set up for ${remainingImages.length} images`);
                        } catch (e) {
                            console.warn('IntersectionObserver setup failed:', e);
                        }
                    }
                    
                    // Periodic check every 250ms (more frequent for better responsiveness)
                    periodicCheckInterval = setInterval(checkAndLoadVisible, 250);
                    console.log('Periodic check started (every 250ms)');
                    
                    // Initial check immediately
                    checkAndLoadVisible();
                    
                    // Fallback: if images still not loaded after 3 seconds, load them all
                    setTimeout(function() {
                        if (periodicCheckInterval) {
                            clearInterval(periodicCheckInterval);
                        }
                        if (quicklookObserver) {
                            quicklookObserver.disconnect();
                        }
                        const finalRemaining = Array.from(document.querySelectorAll('img.lazy-quicklook[data-src]'));
                        console.log(`Fallback: loading ${finalRemaining.length} remaining images`);
                        finalRemaining.forEach(function(img) {
                            const dataSrc = img.getAttribute('data-src');
                            if (dataSrc) {
                                console.log(`Fallback loading: ${dataSrc}`);
                                loadImage(img);
                            }
                        });
                    }, 3000);
                }
            }, 200);
        });
    } catch (error) {
        console.error('Failed to load tiles:', error);
    }
}

// Show tile details
async function showTileDetails(tileCode) {
    try {
        const response = await fetch(`${API_BASE}/tiles/${tileCode}`);
        const data = await response.json();
        
        const modalTitle = document.getElementById('tileModalTitle');
        if (modalTitle) {
            modalTitle.textContent = `Tile ${tileCode}`;
        }
        const modalBody = document.getElementById('tileModalBody');
        if (!modalBody) return;
        
        // Escape values for JavaScript string attributes: replace ' with \' and " with \"
        const tileCodeEscaped = escapeForJs(tileCode);
        
        modalBody.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded">
                <p class="mb-0"><strong>Items:</strong> ${data.item_count} | <strong>Total Images:</strong> ${data.total_image_count}</p>
                <button class="btn btn-danger" onclick="deleteTile('${tileCodeEscaped}')" title="Delete all images for this tile">
                    🗑️ Delete All Images
                </button>
            </div>
            <div class="row">
                ${data.items.map(item => `
                    <div class="col-12 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">${escapeHtml(item.item_id)} (${item.image_count} image(s))</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    ${item.images.map(img => {
                                        const imgItemIdEscaped = escapeForJs(img.item_id);
                                        const previewUrl = `${API_BASE}/tiles/${encodeURIComponent(tileCode)}/images/${encodeURIComponent(img.item_id)}?preview=true`;
                                        const previewUrlEscaped = escapeForJs(previewUrl);
                                        return `
                                        <div class="col-md-6 mb-3">
                                            <div class="border p-2 rounded">
                                                <small class="text-muted d-block mb-2">
                                                    ${img.item_id === item.item_id ? 'Main image' : 'Additional image'}
                                                </small>
                                                <div class="text-center mb-2" style="min-height: 200px; position: relative; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center;">
                                                    <div class="image-placeholder" style="position: absolute; color: #999; font-size: 0.8em;">
                                                        <div class="spinner-border spinner-border-sm" role="status" style="margin-bottom: 5px;">
                                                            <span class="visually-hidden">Loading...</span>
                                                        </div>
                                                        <div>Loading preview...</div>
                                                    </div>
                                                    <img data-src="${previewUrl}" 
                                                         class="image-thumbnail lazy-image" 
                                                         alt="${escapeHtml(img.item_id)}"
                                                         style="max-width: 100%; max-height: 200px; object-fit: contain; cursor: pointer; display: none; position: relative; z-index: 1;"
                                                         onclick="window.open('${previewUrlEscaped}', '_blank')"
                                                         onload="this.style.display='block'; const placeholder = this.previousElementSibling; if(placeholder) placeholder.style.display='none';"
                                                         onerror="this.style.display='none'; const placeholder = this.previousElementSibling; if(placeholder) { placeholder.innerHTML='<div style=\'color: #999;\'>No preview</div>'; }">
                                                    <p class="text-muted small" style="display:none;">Image preview not available</p>
                                                    <a href="${API_BASE}/tiles/${encodeURIComponent(tileCode)}/images/${encodeURIComponent(img.item_id)}" 
                                                       class="btn btn-sm btn-outline-secondary mt-2" 
                                                       download>
                                                        Download Original
                                                    </a>
                                                    <a href="${previewUrl}" 
                                                       class="btn btn-sm btn-outline-primary mt-2" 
                                                       target="_blank">
                                                        View Full Size
                                                    </a>
                                                </div>
                                                <p class="mt-2 mb-1">
                                                    <small>
                                                        Quality Score: ${img.quality_score !== undefined && img.quality_score !== -Infinity ? img.quality_score.toFixed(2) : 'N/A'}<br>
                                                        User Rating: 
                                                        <span class="rating-stars">${getRatingStars(img.user_rating)}</span>
                                                        <button class="btn btn-sm btn-outline-primary ms-2" 
                                                                onclick="rateImage('${tileCodeEscaped}', '${imgItemIdEscaped}')">
                                                            Rate
                                                        </button>
                                                    </small>
                                                </p>
                                                <button class="btn btn-sm btn-danger" 
                                                        onclick="deleteImage('${tileCodeEscaped}', '${imgItemIdEscaped}')">
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    `;
                                    }).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        const modalElement = document.getElementById('tileModal');
        if (!modalElement) return;
        
        // Get existing modal instance or create new one
        let modal = bootstrap.Modal.getInstance(modalElement);
        if (!modal) {
            modal = new bootstrap.Modal(modalElement);
        }
        modal.show();
        
        // Load images lazily after modal is shown (non-blocking)
        // Use a combination of immediate loading, IntersectionObserver, and periodic checks
        setTimeout(function() {
            const modalBodyEl = modalElement.querySelector('.modal-body');
            if (!modalBodyEl) {
                console.warn('Modal body not found for lazy loading');
                return;
            }
            
            const lazyImages = Array.from(modalElement.querySelectorAll('img.lazy-image[data-src]'));
            
            if (lazyImages.length === 0) {
                console.log('No lazy images found in modal');
                return;
            }
            
            console.log(`Found ${lazyImages.length} lazy images in modal`);
            
            // Function to load an image
            function loadModalImage(img) {
                if (!img || !img.getAttribute('data-src')) {
                    return false;
                }
                const dataSrc = img.getAttribute('data-src');
                try {
                    img.src = dataSrc;
                    img.removeAttribute('data-src');
                    console.log('Loaded modal image:', dataSrc);
                    return true;
                } catch (e) {
                    console.error('Error loading modal image:', e);
                    return false;
                }
            }
            
            // Load all visible images immediately
            const visibleImages = [];
            lazyImages.forEach(function(img) {
                try {
                    const rect = img.getBoundingClientRect();
                    const isVisible = rect.top < window.innerHeight + 300 && 
                                     rect.bottom > -300 &&
                                     rect.left < window.innerWidth + 300 &&
                                     rect.right > -300;
                    if (isVisible) {
                        visibleImages.push(img);
                        loadModalImage(img);
                    }
                } catch (e) {
                    console.warn('Error checking image visibility:', e);
                }
            });
            
            console.log(`Loaded ${visibleImages.length} immediately visible images`);
            
            // Get remaining images
            const remainingImages = lazyImages.filter(function(img) {
                return img.getAttribute('data-src') !== null;
            });
            
            if (remainingImages.length > 0) {
                console.log(`${remainingImages.length} images remaining to load`);
                
                // Set up IntersectionObserver
                let imageObserver = null;
                if ('IntersectionObserver' in window) {
                    try {
                        imageObserver = new IntersectionObserver(function(entries, observer) {
                            entries.forEach(function(entry) {
                                if (entry.isIntersecting) {
                                    const img = entry.target;
                                    if (loadModalImage(img)) {
                                        observer.unobserve(img);
                                    }
                                }
                            });
                        }, {
                            root: modalBodyEl,
                            rootMargin: '200px',
                            threshold: 0.01
                        });
                        
                        remainingImages.forEach(function(img) {
                            imageObserver.observe(img);
                        });
                        console.log(`IntersectionObserver set up for ${remainingImages.length} images`);
                    } catch (e) {
                        console.warn('IntersectionObserver setup failed:', e);
                    }
                }
                
                // Periodic check as backup (every 250ms)
                let periodicCheckInterval = setInterval(function() {
                    const stillRemaining = Array.from(modalElement.querySelectorAll('img.lazy-image[data-src]'));
                    
                    if (stillRemaining.length === 0) {
                        console.log('All modal images loaded, stopping periodic check');
                        clearInterval(periodicCheckInterval);
                        if (imageObserver) {
                            imageObserver.disconnect();
                        }
                        return;
                    }
                    
                    stillRemaining.forEach(function(img) {
                        try {
                            const rect = img.getBoundingClientRect();
                            const isVisible = rect.top < window.innerHeight + 300 && 
                                             rect.bottom > -300 &&
                                             rect.left < window.innerWidth + 300 &&
                                             rect.right > -300;
                            if (isVisible) {
                                if (loadModalImage(img)) {
                                    if (imageObserver) {
                                        imageObserver.unobserve(img);
                                    }
                                }
                            }
                        } catch (e) {
                            console.warn('Error in periodic check:', e);
                        }
                    });
                }, 250);
                
                // Fallback: load all remaining images after 3 seconds
                setTimeout(function() {
                    clearInterval(periodicCheckInterval);
                    if (imageObserver) {
                        imageObserver.disconnect();
                    }
                    const finalRemaining = Array.from(modalElement.querySelectorAll('img.lazy-image[data-src]'));
                    console.log(`Fallback: loading ${finalRemaining.length} remaining modal images`);
                    finalRemaining.forEach(function(img) {
                        loadModalImage(img);
                    });
                }, 3000);
            }
        }, 200);
        
        // Ensure backdrop is removed when modal is hidden
        modalElement.addEventListener('hidden.bs.modal', function() {
            // Remove backdrop if it still exists
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            // Remove modal-open class from body
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }, { once: true });
    } catch (error) {
        console.error('Failed to load tile details:', error);
        alert('Failed to load tile details: ' + error.message);
    }
}

// Rate image
async function rateImage(tileCode, itemId) {
    const rating = prompt('Enter rating (0.0 to 5.0):');
    if (rating === null) return;
    
    const ratingNum = parseFloat(rating);
    // Allow 0 as a valid rating (0.0 to 5.0 inclusive)
    if (isNaN(ratingNum) || ratingNum < 0 || ratingNum > 5) {
        alert('Rating must be between 0.0 and 5.0 (0 is allowed)');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tiles/${tileCode}/images/${itemId}/rate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({rating: ratingNum})
        });
        if (response.ok) {
            showTileDetails(tileCode);
        } else {
            alert('Failed to rate image');
        }
    } catch (error) {
        console.error('Failed to rate image:', error);
        alert('Failed to rate image: ' + error.message);
    }
}

// Delete entire tile
async function deleteTile(tileCode) {
    if (!confirm(`Delete all images for tile ${tileCode}? This action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tiles/${tileCode}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        // Close the modal
        const modalElement = document.getElementById('tileModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
            // Ensure backdrop is removed
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }, 300);
        }
        
        // Reload tiles list
        loadTiles();
        if (typeof loadStorageInfo === 'function') {
            loadStorageInfo();
        }
        
        // Show success message
        alert(`Successfully deleted ${result.deleted_count} image(s) from tile ${tileCode}`);
    } catch (error) {
        console.error('Failed to delete tile:', error);
        alert('Failed to delete tile: ' + (error.message || String(error)));
    }
}

// Delete image
async function deleteImage(tileCode, itemId) {
    // Ask for confirmation
    // Note: If user has disabled confirmations in browser, confirm() may return null/undefined
    // In that case, we proceed with deletion (user has chosen to skip confirmations)
    let confirmed = true;
    try {
        const confirmResult = confirm(`Delete image ${itemId}?`);
        // If confirm returns false (user clicked Cancel), abort
        // If confirm returns null/undefined (blocked by browser), proceed anyway
        if (confirmResult === false) {
            return; // User explicitly cancelled
        }
        // If confirmResult is true or null/undefined, proceed with deletion
        confirmed = confirmResult !== false;
    } catch (e) {
        // If confirm() throws an error (blocked by browser), proceed anyway
        console.log('Confirm dialog blocked or unavailable, proceeding with deletion');
        confirmed = true;
    }

    try {
        const response = await fetch(`${API_BASE}/tiles/${tileCode}/images/${itemId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        // Parse response
        const result = await response.json().catch(() => ({}));
        
        // Check if there are still images for this tile
        try {
            const tileResponse = await fetch(`${API_BASE}/tiles/${tileCode}`);
            const tileData = await tileResponse.json();
            
            if (tileData.total_image_count > 0) {
                // Still have images, refresh the modal content
                showTileDetails(tileCode);
            } else {
                // No more images, close the modal
                const modalElement = document.getElementById('tileModal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    } else {
                        // If no instance exists, create one and hide it
                        const newModal = new bootstrap.Modal(modalElement);
                        newModal.hide();
                    }
                    // Ensure backdrop is removed
                    setTimeout(() => {
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) {
                            backdrop.remove();
                        }
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 300);
                }
            }
        } catch (e) {
            // If we can't check, close the modal anyway
            console.warn('Failed to check remaining images, closing modal:', e);
            const modalElement = document.getElementById('tileModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                // Ensure backdrop is removed
                setTimeout(() => {
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }, 300);
            }
        }
        
        // Reload tiles list to reflect the deletion
        loadTiles();
    } catch (error) {
        console.error('Failed to delete image:', error);
        alert('Failed to delete image: ' + (error.message || String(error)));
    }
}

// Global event listener to ensure backdrop is always removed
document.addEventListener('DOMContentLoaded', function() {
    // Listen for modal hidden events
    document.addEventListener('hidden.bs.modal', function() {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    });
});

