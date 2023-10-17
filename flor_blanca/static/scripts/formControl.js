document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("questionForm");
  const submitBtn = document.getElementById("submitBtn");
  const toast = document.getElementById("toastAlert");
  const countSpan = document.querySelector(".countSpan");
  let toastTimeout;

  const submitRating = document.querySelectorAll(".submitRating");
  const ratingForm = document.querySelectorAll(".my-form");

  const showToast = () => {
    toast.classList.remove("hide");
    if (toastTimeout) {
      clearTimeout(toastTimeout);
    }
    toastTimeout = setTimeout(() => {
      toast.classList.add("hide");
      toastTimeout = null;
    }, 4000);
  };

  const getQuestionCount = async () => {
    try {
      const paramValue = form.getAttribute("data-endpoint");
      const req = await fetch(`/questions/count?questionType=${paramValue}`);

      if (!req.ok) throw new Error();
      const response = await req.json();

      if (countSpan) {
        let count = parseInt(response["count"]);
        countSpan.textContent = count;
      }
    } catch (err) {
      console.log(err.message);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const URL = form.getAttribute("action");
    let count = parseInt(countSpan.textContent);

    if (count > 0) {
      submitBtn.textContent = "Enviando...";
      submitBtn.setAttribute("disabled", "true");
      toast.textContent = "Enviando tu pregunta...";
      showToast();
      try {
        const request = await fetch(URL, {
          method: "POST",
          body: data,
        });
        if (!request.ok) throw new Error();
        const response = await request.json();
        toast.textContent = response.message;
        showToast();
        countSpan.textContent = response.count;
      } catch (err) {
        toast.textContent =
          "Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.";
        showToast();
        console.log(err.message);
      } finally {
        submitBtn.textContent = "Enviar";
        submitBtn.removeAttribute("disabled");
        form.reset();
      }
    } else {
      toast.textContent = "Has usado el máximo de preguntas por mes.";
      showToast();
      form.reset();
    }
  };
  if (form) {
    form.addEventListener("submit", handleSubmit);
    getQuestionCount();
  }

  const handleRating = async (event) => {
    event.preventDefault();
    const form = event.target;
    const URL = form.getAttribute("action");
    const data = new FormData(form);
    toast.textContent = "Gracias por tu opinión";
    showToast();
    try {
      const request = await fetch(URL, {
        method: "POST",
        body: data,
      });
      if (!request.ok) throw new Error();
      const response = await request.json();
      toast.textContent = response.message;
      showToast();
    } catch (err) {
      toast.textContent =
        "Ha ocurrido un error en el proceso. Por favor pruebe más tarde.";
      showToast();
      console.log(err.message);
    } finally {
      form.classList.add("d-none");
      form.reset();
    }
  };
  if (ratingForm) {
    ratingForm.forEach((button) => {
      button.addEventListener("submit", handleRating);
    });
  }
});
