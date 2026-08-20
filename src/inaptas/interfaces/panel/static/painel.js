document.addEventListener("click", (event) => {
  const alvo = event.target.closest("[data-confirm]");
  if (alvo && !window.confirm(alvo.dataset.confirm)) {
    event.preventDefault();
  }
});
