// ROI Map Management for GRI Resolver Web Interface

// ROI map variables
let roiMap = null;
let drawnItems = null;
let drawControl = null;
let currentRectangle = null;
let kmlLayer = null;
let baseMaps = null;
let overlayMaps = null;

// Initialize ROI map
function initROIMap() {
    // Check if map container exists
    const mapContainer = document.getElementById('roiMap');
    if (!mapContainer) {
        console.warn('ROI map container not found');
        return;
    }
    
    // If map already exists, just invalidate size and ensure controls are present
    if (roiMap) {
        roiMap.invalidateSize();
        // Ensure drawnItems exists
        if (!drawnItems) {
            drawnItems = new L.FeatureGroup();
            roiMap.addLayer(drawnItems);
        }
        
        // Remove existing event listeners to avoid duplicates
        roiMap.off(L.Draw.Event.CREATED);
        roiMap.off(L.Draw.Event.DELETED);
        roiMap.off(L.Draw.Event.EDITED);
        
        // Re-attach event listeners
        roiMap.on(L.Draw.Event.CREATED, function (e) {
            const layer = e.layer;
            drawnItems.addLayer(layer);
            
            // Remove previous rectangle if exists
            if (currentRectangle) {
                drawnItems.removeLayer(currentRectangle);
            }
            currentRectangle = layer;
            
            // Update input fields
            const bounds = layer.getBounds();
            const minLonEl = document.getElementById('minLon');
            const minLatEl = document.getElementById('minLat');
            const maxLonEl = document.getElementById('maxLon');
            const maxLatEl = document.getElementById('maxLat');
            
            if (minLonEl) minLonEl.value = bounds.getWest().toFixed(4);
            if (minLatEl) minLatEl.value = bounds.getSouth().toFixed(4);
            if (maxLonEl) maxLonEl.value = bounds.getEast().toFixed(4);
            if (maxLatEl) maxLatEl.value = bounds.getNorth().toFixed(4);
        });
        
        roiMap.on(L.Draw.Event.DELETED, function (e) {
            currentRectangle = null;
            const minLonEl = document.getElementById('minLon');
            const minLatEl = document.getElementById('minLat');
            const maxLonEl = document.getElementById('maxLon');
            const maxLatEl = document.getElementById('maxLat');
            
            if (minLonEl) minLonEl.value = '';
            if (minLatEl) minLatEl.value = '';
            if (maxLonEl) maxLonEl.value = '';
            if (maxLatEl) maxLatEl.value = '';
        });
        
        roiMap.on(L.Draw.Event.EDITED, function (e) {
            const layers = e.layers;
            layers.eachLayer(function (layer) {
                if (layer === currentRectangle) {
                    const bounds = layer.getBounds();
                    const minLonEl = document.getElementById('minLon');
                    const minLatEl = document.getElementById('minLat');
                    const maxLonEl = document.getElementById('maxLon');
                    const maxLatEl = document.getElementById('maxLat');
                    
                    if (minLonEl) minLonEl.value = bounds.getWest().toFixed(4);
                    if (minLatEl) minLatEl.value = bounds.getSouth().toFixed(4);
                    if (maxLonEl) maxLonEl.value = bounds.getEast().toFixed(4);
                    if (maxLatEl) maxLatEl.value = bounds.getNorth().toFixed(4);
                }
            });
        });
        
        // Ensure baseMaps and overlayMaps are initialized
        if (!baseMaps) {
            baseMaps = {
                "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                })
            };
        }
        if (!overlayMaps) {
            // Create empty layer group for MGRS tiles (will be populated after KML loads)
            const emptyMGRSLayer = L.layerGroup();
            overlayMaps = {
                "MGRS Tiles": emptyMGRSLayer
            };
            // Add empty layer group to map so it appears in layer control
            emptyMGRSLayer.addTo(roiMap);
        }
        
        // Check if layer control exists, if not add it
        // Also check if there are multiple layer controls (shouldn't happen, but just in case)
        if (!roiMap._layersControl) {
            // Check if there's already a layer control in the DOM
            const existingControls = document.querySelectorAll('.leaflet-control-layers');
            if (existingControls.length > 0) {
                console.warn('Layer control already exists in DOM but not in map object');
                // Try to find and remove duplicate controls
                for (let i = 1; i < existingControls.length; i++) {
                    existingControls[i].remove();
                }
            }
            const layerControl = L.control.layers(baseMaps, overlayMaps, {
                collapsed: false
            });
            layerControl.addTo(roiMap);
        } else {
            // Layer control exists, but check for duplicates in DOM
            const existingControls = document.querySelectorAll('.leaflet-control-layers');
            if (existingControls.length > 1) {
                console.warn('Multiple layer controls found, removing duplicates');
                // Keep the first one, remove the rest
                for (let i = 1; i < existingControls.length; i++) {
                    existingControls[i].remove();
                }
            }
        }
        
        // Check if draw control exists, if not add it
        if (!drawControl) {
            drawControl = new L.Control.Draw({
                draw: {
                    polygon: false,
                    polyline: false,
                    circle: false,
                    circlemarker: false,
                    marker: false,
                    rectangle: {
                        shapeOptions: {
                            color: '#3388ff',
                            fillColor: '#3388ff',
                            fillOpacity: 0.2
                        }
                    }
                },
                edit: {
                    featureGroup: drawnItems,
                    remove: true
                }
            });
            roiMap.addControl(drawControl);
        }
        
        // Force map to update after adding controls
        setTimeout(function() {
            if (roiMap) {
                roiMap.invalidateSize();
            }
        }, 50);
        
        // Ensure KML layer is loaded
        if (!kmlLayer) {
            setTimeout(function() {
                loadKMLTiles();
            }, 100);
        }
        
        return;
    }
    
    // Create map centered on Europe/Africa
    roiMap = L.map('roiMap').setView([20, 0], 2);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(roiMap);
    
    // Initialize the feature group to store editable layers
    drawnItems = new L.FeatureGroup();
    roiMap.addLayer(drawnItems);
    
    // Add layer control
    baseMaps = {
        "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        })
    };
    
    // Create empty layer group for MGRS tiles (will be populated after KML loads)
    // Don't add it to map yet - it will be added when KML tiles are loaded
    const emptyMGRSLayer = L.layerGroup();
    overlayMaps = {
        "MGRS Tiles": emptyMGRSLayer
    };
    
    // Check for duplicate layer controls before creating a new one
    const existingControls = document.querySelectorAll('.leaflet-control-layers');
    if (existingControls.length > 0) {
        console.warn('Layer control already exists in DOM, removing duplicates');
        // Remove all existing layer controls
        existingControls.forEach(control => control.remove());
    }
    
    L.control.layers(baseMaps, overlayMaps, {
        collapsed: false
    }).addTo(roiMap);
    
    // Load and add KML layer with MGRS tiles (after a short delay to ensure map is ready)
    setTimeout(function() {
        loadKMLTiles();
    }, 100);
    
    // Remove existing event listeners to avoid duplicates
    if (roiMap) {
        roiMap.off(L.Draw.Event.CREATED);
        roiMap.off(L.Draw.Event.DELETED);
        roiMap.off(L.Draw.Event.EDITED);
    }
    
    // Initialize the draw control and pass it the FeatureGroup of editable layers
    // Remove existing control if it exists
    if (drawControl) {
        try {
            roiMap.removeControl(drawControl);
        } catch (e) {
            // Ignore if control doesn't exist
        }
    }
    
    drawControl = new L.Control.Draw({
        draw: {
            polygon: false,
            polyline: false,
            circle: false,
            circlemarker: false,
            marker: false,
            rectangle: {
                shapeOptions: {
                    color: '#3388ff',
                    fillColor: '#3388ff',
                    fillOpacity: 0.2
                }
            }
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    roiMap.addControl(drawControl);
    
    // Handle rectangle creation
    roiMap.on(L.Draw.Event.CREATED, function (e) {
        const layer = e.layer;
        drawnItems.addLayer(layer);
        
        // Remove previous rectangle if exists
        if (currentRectangle) {
            drawnItems.removeLayer(currentRectangle);
        }
        currentRectangle = layer;
        
        // Update input fields
        const bounds = layer.getBounds();
        const minLonEl = document.getElementById('minLon');
        const minLatEl = document.getElementById('minLat');
        const maxLonEl = document.getElementById('maxLon');
        const maxLatEl = document.getElementById('maxLat');
        
        if (minLonEl) minLonEl.value = bounds.getWest().toFixed(4);
        if (minLatEl) minLatEl.value = bounds.getSouth().toFixed(4);
        if (maxLonEl) maxLonEl.value = bounds.getEast().toFixed(4);
        if (maxLatEl) maxLatEl.value = bounds.getNorth().toFixed(4);
    });
    
    // Handle rectangle deletion
    roiMap.on(L.Draw.Event.DELETED, function (e) {
        currentRectangle = null;
        const minLonEl = document.getElementById('minLon');
        const minLatEl = document.getElementById('minLat');
        const maxLonEl = document.getElementById('maxLon');
        const maxLatEl = document.getElementById('maxLat');
        
        if (minLonEl) minLonEl.value = '';
        if (minLatEl) minLatEl.value = '';
        if (maxLonEl) maxLonEl.value = '';
        if (maxLatEl) maxLatEl.value = '';
    });
    
    // Handle rectangle editing
    roiMap.on(L.Draw.Event.EDITED, function (e) {
        const layers = e.layers;
        layers.eachLayer(function (layer) {
            if (layer === currentRectangle) {
                const bounds = layer.getBounds();
                const minLonEl = document.getElementById('minLon');
                const minLatEl = document.getElementById('minLat');
                const maxLonEl = document.getElementById('maxLon');
                const maxLatEl = document.getElementById('maxLat');
                
                if (minLonEl) minLonEl.value = bounds.getWest().toFixed(4);
                if (minLatEl) minLatEl.value = bounds.getSouth().toFixed(4);
                if (maxLonEl) maxLonEl.value = bounds.getEast().toFixed(4);
                if (maxLatEl) maxLatEl.value = bounds.getNorth().toFixed(4);
            }
        });
    });
    
    // Force map to update after adding control
    setTimeout(function() {
        if (roiMap) {
            roiMap.invalidateSize();
        }
    }, 50);
}

// Load KML tiles layer (using optimized GeoJSON endpoint)
async function loadKMLTiles() {
    if (!roiMap) return;
    
    try {
        // Remove existing KML layer if present
        if (kmlLayer) {
            roiMap.removeLayer(kmlLayer);
        }
        
        // Show loading indicator
        console.log('Loading MGRS tiles (this may take a moment for the first load)...');
        
        // Fetch simplified GeoJSON instead of KML for faster loading
        const response = await fetch(`${API_BASE}/geojson/tiles`);
        if (!response.ok) {
            console.warn('Failed to load GeoJSON tiles, falling back to KML:', response.statusText);
            // Fallback to KML if GeoJSON fails
            const kmlResponse = await fetch(`${API_BASE}/kml/tiles`);
            if (!kmlResponse.ok) {
                console.error('Failed to load KML tiles:', kmlResponse.statusText);
                return;
            }
            const kmlText = await kmlResponse.text();
            const parser = new DOMParser();
            const kml = parser.parseFromString(kmlText, 'text/xml');
            const geojson = toGeoJSON.kml(kml);
            createGeoJSONLayer(geojson);
            return;
        }
        
        // Parse GeoJSON directly (much faster than KML)
        const geojson = await response.json();
        createGeoJSONLayer(geojson);
        
    } catch (error) {
        console.error('Error loading tiles:', error);
    }
}

// Helper function to create GeoJSON layer with viewport-based rendering
function createGeoJSONLayer(geojson) {
    // Store all features for viewport filtering
    const allFeatures = geojson.features || [];
    console.log(`Creating GeoJSON layer with ${allFeatures.length} features`);
    
    if (allFeatures.length === 0) {
        console.warn('No features found in GeoJSON');
        return;
    }
    
    // Function to filter features by viewport
    function getVisibleFeatures(bounds) {
        if (!bounds) return allFeatures;
        return allFeatures.filter(function(feature) {
            if (!feature.geometry || !feature.geometry.coordinates) return false;
            const coords = feature.geometry.coordinates[0]; // First ring of polygon
            // Check if any point of the polygon is in viewport
            for (let i = 0; i < coords.length; i++) {
                const [lon, lat] = coords[i];
                if (bounds.contains([lat, lon])) {
                    return true;
                }
            }
            // Also check if viewport intersects with polygon bounds
            let minLat = Infinity, maxLat = -Infinity, minLon = Infinity, maxLon = -Infinity;
            for (let i = 0; i < coords.length; i++) {
                const [lon, lat] = coords[i];
                minLat = Math.min(minLat, lat);
                maxLat = Math.max(maxLat, lat);
                minLon = Math.min(minLon, lon);
                maxLon = Math.max(maxLon, lon);
            }
            return !(maxLon < bounds.getWest() || minLon > bounds.getEast() || 
                     maxLat < bounds.getSouth() || minLat > bounds.getNorth());
        });
    }
    
    // Create a layer group that will be updated based on viewport
    const layerGroup = L.layerGroup();
    
    function updateVisibleTiles() {
        if (!roiMap) {
            console.warn('updateVisibleTiles: roiMap is null');
            return;
        }
        // Only update if the layer group is actually on the map
        if (!roiMap.hasLayer(layerGroup)) {
            console.warn('updateVisibleTiles: layerGroup is not on map');
            return;
        }
        const bounds = roiMap.getBounds();
        const visibleFeatures = getVisibleFeatures(bounds);
        console.log(`updateVisibleTiles: found ${visibleFeatures.length} visible features`);
        
        // Clear existing layers
        layerGroup.clearLayers();
        
        // Add only visible features
        const visibleLayer = L.geoJSON(visibleFeatures, {
            style: function(feature) {
                return {
                    color: '#0066ff',
                    weight: 1,
                    opacity: 0.6,
                    fillColor: '#0066ff',
                    fillOpacity: 0.1
                };
            },
            onEachFeature: function(feature, layer) {
                // Add popup with tile information if available
                if (feature.properties && feature.properties.name) {
                    layer.bindPopup(feature.properties.name);
                    
                    // Calculate center of polygon for label placement
                    if (feature.geometry && feature.geometry.coordinates && feature.geometry.coordinates[0]) {
                        const coords = feature.geometry.coordinates[0];
                        let sumLat = 0, sumLon = 0, count = 0;
                        for (let i = 0; i < coords.length; i++) {
                            const [lon, lat] = coords[i];
                            sumLat += lat;
                            sumLon += lon;
                            count++;
                        }
                        if (count > 0) {
                            const centerLat = sumLat / count;
                            const centerLon = sumLon / count;
                            
                            // Create a label at the center
                            const labelText = feature.properties.name || '';
                            // Calculate approximate size for proper centering
                            const textLength = labelText.length;
                            const estimatedWidth = textLength * 6 + 8; // Approximate width in pixels
                            const estimatedHeight = 20; // Approximate height in pixels
                            
                            const label = L.marker([centerLat, centerLon], {
                                icon: L.divIcon({
                                    className: 'mgrs-tile-label',
                                    html: '<div style="background-color: rgba(255,255,255,0.8); padding: 2px 4px; border-radius: 3px; font-size: 10px; font-weight: bold; color: #0066ff; border: 1px solid #0066ff; pointer-events: none; white-space: nowrap; display: inline-block; text-align: center; line-height: 1.2;">' + labelText + '</div>',
                                    iconSize: [estimatedWidth, estimatedHeight],
                                    iconAnchor: [estimatedWidth / 2, estimatedHeight / 2]
                                })
                            });
                            label.addTo(layerGroup);
                        }
                    }
                }
            }
        });
        
        visibleLayer.addTo(layerGroup);
    }
    
    // Update on map move/zoom (with debouncing) - only when layer is on map
    let updateTimeout = null;
    function scheduleUpdate() {
        if (updateTimeout) clearTimeout(updateTimeout);
        updateTimeout = setTimeout(function() {
            if (roiMap && roiMap.hasLayer(layerGroup)) {
                updateVisibleTiles();
            }
        }, 100);
    }
    
    // Store update function for use in event listeners
    const scheduleUpdateRef = scheduleUpdate;
    
    // Initial update (but don't add to map yet - user will toggle it via layer control)
    // We need to initialize the layer group structure, but updateVisibleTiles will only
    // add layers when the layer group is actually on the map
    kmlLayer = layerGroup;
    
    // Update layer control with KML layer
    if (baseMaps && overlayMaps) {
        // Replace the empty layer group with the actual KML layer
        const oldLayerGroup = overlayMaps["MGRS Tiles"];
        overlayMaps["MGRS Tiles"] = kmlLayer;
        
        // Remove old layer from map if it was added
        if (oldLayerGroup && oldLayerGroup instanceof L.LayerGroup) {
            if (roiMap.hasLayer(oldLayerGroup)) {
                roiMap.removeLayer(oldLayerGroup);
            }
        }
        
        // Remove the old layer control completely
        const layerControl = roiMap._layersControl;
        if (layerControl) {
            roiMap.removeControl(layerControl);
            // Also remove from DOM to ensure it's completely gone
            const controlElement = layerControl.getContainer();
            if (controlElement && controlElement.parentNode) {
                controlElement.parentNode.removeChild(controlElement);
            }
        }
        
        // Also check for any remaining layer controls in DOM and remove them
        const existingControls = document.querySelectorAll('.leaflet-control-layers');
        existingControls.forEach(control => {
            if (control.parentNode) {
                control.parentNode.removeChild(control);
            }
        });
        
        // Create new layer control with updated overlay
        const newLayerControl = L.control.layers(baseMaps, overlayMaps, {
            collapsed: false
        });
        newLayerControl.addTo(roiMap);
        
        console.log('Old layer control removed and new one created with MGRS tiles layer');
    }
    
    // Listen for when the layer is added/removed from the map via layer control
    kmlLayer.on('add', function() {
        console.log('MGRS layer added to map');
        // When layer is added to map (user checked the box), update visible tiles
        // Use a small delay to ensure the layer is fully added
        setTimeout(function() {
            if (roiMap && roiMap.hasLayer(layerGroup)) {
                updateVisibleTiles();
                // Also attach move/zoom listeners when layer is added
                roiMap.on('moveend', scheduleUpdateRef);
                roiMap.on('zoomend', scheduleUpdateRef);
            }
        }, 50);
    });
    
    kmlLayer.on('remove', function() {
        console.log('MGRS layer removed from map');
        // When layer is removed from map (user unchecked the box), clear layers
        layerGroup.clearLayers();
        // Remove move/zoom listeners when layer is removed
        roiMap.off('moveend', scheduleUpdateRef);
        roiMap.off('zoomend', scheduleUpdateRef);
    });
    
    console.log(`MGRS tiles loaded successfully (${allFeatures.length} total tiles, viewport-based rendering enabled)`);
}

// Update map from input fields
function updateMapFromInputs() {
    const minLon = parseFloat(document.getElementById('minLon').value);
    const minLat = parseFloat(document.getElementById('minLat').value);
    const maxLon = parseFloat(document.getElementById('maxLon').value);
    const maxLat = parseFloat(document.getElementById('maxLat').value);
    
    if (isNaN(minLon) || isNaN(minLat) || isNaN(maxLon) || isNaN(maxLat)) {
        return;
    }
    
    if (!roiMap) {
        initROIMap();
    }
    
    // Remove existing rectangle
    if (currentRectangle) {
        drawnItems.removeLayer(currentRectangle);
    }
    
    // Create new rectangle from inputs
    const bounds = [[minLat, minLon], [maxLat, maxLon]];
    currentRectangle = L.rectangle(bounds, {
        color: '#3388ff',
        fillColor: '#3388ff',
        fillOpacity: 0.2
    });
    drawnItems.addLayer(currentRectangle);
    
    // Fit map to bounds
    roiMap.fitBounds(bounds);
}

// Clear ROI selection
function clearROI() {
    if (currentRectangle) {
        drawnItems.removeLayer(currentRectangle);
        currentRectangle = null;
    }
    document.getElementById('minLon').value = '';
    document.getElementById('minLat').value = '';
    document.getElementById('maxLon').value = '';
    document.getElementById('maxLat').value = '';
}

// Initialize map when ROI tab is shown
document.addEventListener('DOMContentLoaded', function() {
    const roiTab = document.getElementById('roi-tab');
    if (roiTab) {
        roiTab.addEventListener('shown.bs.tab', function() {
            // Small delay to ensure tab is visible before initializing map
            setTimeout(function() {
                if (!roiMap) {
                    initROIMap();
                } else {
                    roiMap.invalidateSize(); // Resize map if tab was hidden
                    // Ensure controls are present and visible
                    if (drawControl) {
                        // Check if control is already on map by looking for its container
                        const drawContainer = document.querySelector('.leaflet-draw');
                        if (!drawContainer) {
                            roiMap.addControl(drawControl);
                        }
                    }
                    // Layer control should already be added, just ensure it's visible
                    if (roiMap._layersControl) {
                        roiMap.invalidateSize();
                    }
                }
            }, 100);
        });
        
        // Also initialize if ROI tab is already active on page load
        const roiPane = document.getElementById('roi');
        if (roiPane && roiPane.classList.contains('active')) {
            setTimeout(function() {
                if (!roiMap) {
                    initROIMap();
                }
            }, 200);
        }
    }
});

