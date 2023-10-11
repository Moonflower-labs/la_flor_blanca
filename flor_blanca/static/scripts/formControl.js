document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("questionForm");
  const submitBtn = document.getElementById("submitBtn");

  formControl = () => {
    submitBtn.setAttribute("disabled", "true");
    submitBtn.textContent = "Enviando...";
  };

  if (form) form.addEventListener("submit", formControl);
});
