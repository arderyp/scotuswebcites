document.addEventListener('DOMContentLoaded', () => {
    const tableRows = document.querySelectorAll('tbody tr');
    
    // 1. Update Badge Counts
    const filters = [
        { 
            badge: document.getElementById('filter-all-count'), 
            count: tableRows.length 
        },
        { 
            badge: document.getElementById('filter-citations-count'), 
            count: document.querySelectorAll('tr.has-citations').length 
        },
        { 
            badge: document.getElementById('filter-revisions-count'), 
            count: document.querySelectorAll('tr.revision').length 
        },
    ];

    filters.forEach(f => {
        if (f.badge) {
            f.badge.textContent = f.count;
            // Update classes (adjust labels if you've fully removed Bootstrap)
            if (f.count > 0) {
                f.badge.classList.add('label', 'label-primary', 'label-as-badge');
                f.badge.classList.remove('badge');
            } else {
                f.badge.classList.add('badge');
                f.badge.classList.remove('label', 'label-primary', 'label-as-badge');
            }
        }
    });

    // 2. Show filter container
    const filterContainer = document.getElementById('javascript-filters');
    if (filterContainer) filterContainer.style.display = 'block';

    // 3. Filtering Logic
    const applyFilter = (selector) => {
        tableRows.forEach(row => {
            if (!selector) {
                row.style.display = ''; // Show all
            } else {
                row.style.display = row.matches(selector) ? '' : 'none';
            }
        });
    };

    // 4. Event Listeners
    document.getElementById('filter-all')?.addEventListener('click', (e) => {
        e.preventDefault();
        applyFilter();
    });

    document.getElementById('filter-citations')?.addEventListener('click', (e) => {
        e.preventDefault();
        applyFilter('tr.has-citations');
    });

    document.getElementById('filter-revisions')?.addEventListener('click', (e) => {
        e.preventDefault();
        applyFilter('tr.revision');
    });
});