document.querySelectorAll('.carousel-indicators button').forEach((btn, idx) => {
  btn.addEventListener('click', () => {
    const container = document.getElementById('scotusCarousel');
    const slideWidth = container.offsetWidth;
    container.scrollTo({
      left: slideWidth * idx,
      behavior: 'smooth'
    });
  });
});
