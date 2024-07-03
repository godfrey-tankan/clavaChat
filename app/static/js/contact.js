function sendMail(event) {
  // Prevent default form submission behavior
  event.preventDefault();

  const successAlert = document.getElementById("alert-success");
  const errorAlert = document.getElementById("alert-error");
  const submitButton = document.getElementById("submit-btn");

  const form = document.getElementById("send-email");

  // Get the required form fields
  const nameInput = form.querySelector("#name").value;
  const emailInput = form.querySelector("#email").value;
  const messageInput = form.querySelector("#message").value;
  // Show the submit button
  if (submitButton.textContent === "SEND") {
    submitButton.textContent = "sending...";
    setTimeout(function () {
      submitButton.textContent = "SEND";
    }, 2000); // 1000 milliseconds = 1 second
  } else if (submitButton.textContent === "SUBMIT") {
    submitButton.textContent = "submitting...";
    setTimeout(function () {
      submitButton.textContent = "SUBMIT";
    }, 2000); // 1000 milliseconds = 1 second
  } else {
    submitButton.textContent = "SEND";
    setTimeout(function () {
      submitButton.textContent = "SEND";
    }, 2000);
  }

  if (
    nameInput.value === "" ||
    emailInput.value === "" ||
    messageInput.value === ""
  ) {
    errorAlert.style.display = "block";
    setTimeout(() => {
      errorAlert.style.display = "none";
    }, 2000);
    return;
  }
  emailjs.sendForm("service_7rfvwkn", "template_2u09n2j", form).then(
    (response) => {
      successAlert.style.display = "block";
      setTimeout(() => {
        successAlert.style.display = "none";
      }, 2000);
    },
    (error) => {
      console.log("FAILED...", error);
    }
  );
}
