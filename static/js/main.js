document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.link');
  links.forEach(l => {
    l.addEventListener('mouseenter', () => l.classList.add('active'));
    l.addEventListener('mouseleave', () => l.classList.remove('active'));
  });
});
