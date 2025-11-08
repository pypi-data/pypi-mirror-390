// Navigation Management for GRI Resolver Web Interface

// Section IDs
const SECTIONS = {
    tiles: 'tilesSection',
    downloads: 'downloadsSection',
    storage: 'storageSection'
};

// Current active section
let currentSection = 'tiles'; // Default to tiles (main section)

// Show a specific section and hide others
function showSection(sectionId) {
    // Hide all sections
    Object.values(SECTIONS).forEach(section => {
        const el = document.getElementById(section);
        if (el) {
            el.style.display = 'none';
        }
    });
    
    // Show requested section
    const targetSection = document.getElementById(SECTIONS[sectionId]);
    if (targetSection) {
        targetSection.style.display = 'block';
        currentSection = sectionId;
        
        // Update URL hash without triggering scroll
        if (history.pushState) {
            history.pushState(null, null, '#' + sectionId);
        } else {
            window.location.hash = sectionId;
        }
        
        // Update active nav link
        updateActiveNavLink(sectionId);
        
        // Trigger section-specific initialization if needed
        initializeSection(sectionId);
    }
}

// Update active navigation link
function updateActiveNavLink(sectionId) {
    // Remove active class from all nav links
    document.querySelectorAll('.main-nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current nav link
    const activeLink = document.getElementById(`nav-${sectionId}`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Initialize section-specific functionality
function initializeSection(sectionId) {
    switch(sectionId) {
        case 'tiles':
            // Load tiles if not already loaded
            if (typeof loadTiles === 'function') {
                const tilesList = document.getElementById('tilesList');
                if (tilesList && (!tilesList.innerHTML || tilesList.innerHTML.includes('Loading tiles'))) {
                    loadTiles();
                }
            }
            break;
        case 'downloads':
            // Load regions if not already loaded
            if (typeof loadRegions === 'function') {
                const regionSelect = document.getElementById('regionSelect');
                if (regionSelect && regionSelect.options.length <= 1) {
                    loadRegions();
                }
            }
            // Initialize ROI map if needed
            if (typeof initROIMap === 'function') {
                const roiMapContainer = document.getElementById('roiMap');
                if (roiMapContainer && !roiMap) {
                    // Map will be initialized when ROI tab is shown
                }
            }
            break;
        case 'storage':
            // Load storage info
            if (typeof loadStorageInfo === 'function') {
                const storageInfo = document.getElementById('storageInfo');
                if (storageInfo && (!storageInfo.innerHTML || storageInfo.innerHTML.includes('Loading storage'))) {
                    loadStorageInfo();
                }
            }
            break;
    }
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check URL hash for initial section
    const hash = window.location.hash.replace('#', '');
    if (hash && SECTIONS[hash]) {
        showSection(hash);
    } else {
        // Default to tiles section
        showSection('tiles');
    }
    
    // Listen for hash changes (browser back/forward)
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.replace('#', '');
        if (hash && SECTIONS[hash]) {
            showSection(hash);
        }
    });
});

