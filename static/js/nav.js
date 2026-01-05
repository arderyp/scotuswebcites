/**
* Toggles active state for a group of buttons.
* @param {HTMLElement} activeElement - The button/link to make solid.
* @param {string} parentSelector - The container ID/class to scope the change.
*/
function setActiveItem(activeElement, parentSelector) {
const group = document.querySelector(parentSelector);
if (!group) return;

// Reset all items in this group to 'outline'
group.querySelectorAll('[role="button"], button, a').forEach(item => {
  item.classList.add('outline');
  item.removeAttribute('aria-current');
});

// Make the clicked/active item solid
activeElement.classList.remove('outline');
activeElement.setAttribute('aria-current', 'true');
}

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Handle Navigation (URL-based) ---
    const currentPath = window.location.pathname;
    const navButtons = document.querySelectorAll('#nav-group button');
    navButtons.forEach(btn => {
        const onClickAttr = btn.getAttribute('onclick') || "";

        // Check if the current URL path exists within the onclick string
        // We use a specific check to avoid partial matches (e.g., '/' matching '/citations/')
        if (onClickAttr.includes(`'${currentPath}'`) || onClickAttr.includes(`"${currentPath}"`)) {
            setActiveItem(btn, '#nav-group');
        }
    });

    // --- 2. Handle Filters (Event-based) ---
    const filterGroup = document.querySelector('#javascript-filters fieldset');
    if (filterGroup) {
      filterGroup.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (btn) {
          setActiveItem(btn, '#javascript-filters fieldset');
        }
      });

      // Optional: Ensure "All" starts as active if not already set
      const allBtn = document.getElementById('filter-all');
      if (allBtn) setActiveItem(allBtn, '#javascript-filters fieldset');
    }
});