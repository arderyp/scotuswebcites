document.addEventListener('DOMContentLoaded', () => {
    const tableRows = document.querySelectorAll('tbody tr');
    const statusA = document.querySelectorAll('.status-a');
    const statusR = document.querySelectorAll('.status-r');
    const statusU = document.querySelectorAll('.status-u');

    // 1. Update Badge Counts and Classes
    const filters = [
        { badge: document.getElementById('filter-all-count'), count: tableRows.length },
        { badge: document.getElementById('filter-available-count'), count: statusA.length },
        { badge: document.getElementById('filter-redirect-count'), count: statusR.length },
        { badge: document.getElementById('filter-unavailable-count'), count: statusU.length },
    ];

    filters.forEach(f => {
        if (f.badge) {
            f.badge.textContent = f.count;
            // Since you are dropping Bootstrap, use Pico.css logic or simple classes
            if (f.count > 0) {
                f.badge.className = 'label label-primary label-as-badge';
            } else {
                f.badge.className = 'badge';
            }
        }
    });

    // 2. Show the filter container
    const jsFilters = document.getElementById('javascript-filters');
    if (jsFilters) jsFilters.style.display = 'block';

    // 3. Helper function for filtering
    const filterRows = (selector) => {
        tableRows.forEach(row => {
            if (!selector) {
                row.style.display = ''; // Show all
            } else {
                // Check if row contains an element matching the status selector
                row.style.display = row.querySelector(selector) ? '' : 'none';
            }
        });
    };

    // 4. Click Events
    document.getElementById('filter-all')?.addEventListener('click', () => filterRows());
    document.getElementById('filter-available')?.addEventListener('click', () => filterRows('.status-a'));
    document.getElementById('filter-redirect')?.addEventListener('click', () => filterRows('.status-r'));
    document.getElementById('filter-unavailable')?.addEventListener('click', () => filterRows('.status-u'));
});