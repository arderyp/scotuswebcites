document.addEventListener('DOMContentLoaded', () => {
    const tableRows = document.querySelectorAll('tbody tr');
    const filterMenus = document.querySelectorAll('.js-filter-dropdown');

    filterMenus.forEach(menu => {
        // 1. Update Counts dynamically based on data-count-type
        const badges = menu.querySelectorAll('.count-badge');
        badges.forEach(badge => {
            const selector = badge.getAttribute('data-count-type');
            let count = 0;

            if (selector === 'all') {
                count = tableRows.length;
            } else {
                // Count how many rows contain an element matching the selector
                count = Array.from(tableRows).filter(row => row.querySelector(selector)).length;
            }
            badge.textContent = `(${count})`;
        });

        // 2. Show the menu
        menu.style.display = 'block';

        // 3. Generic Click Logic
        menu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const selector = link.getAttribute('data-value');
                const summary = menu.querySelector('summary');

                // Update Summary text
                summary.textContent = link.childNodes[0].textContent.trim();

                // Apply filtering
                tableRows.forEach(row => {
                    if (selector === 'all' || !selector) {
                        row.style.display = '';
                    } else {
                        row.style.display = row.querySelector(selector) ? '' : 'none';
                    }
                });

                menu.removeAttribute('open');
            });
        });
    });
});