document.querySelectorAll('.carousel-indicators button').forEach((btn, idx) => {
  btn.addEventListener('click', () => {
    const container = document.querySelector('.carousel-inner');
    const slideWidth = container.offsetWidth;
    container.scrollTo({
      left: slideWidth * idx,
      behavior: 'smooth'
    });
    
    // ACCESSIBILITY
    const parentNav = btn.closest('.carousel-indicators');
    parentNav.querySelectorAll('button').forEach((b, i) => {
      b.setAttribute('aria-selected', i === idx ? 'true' : 'false');
    });
  });
});
