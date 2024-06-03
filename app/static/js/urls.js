document.addEventListener("DOMContentLoaded", function () {
  const loginButton = document.getElementById("login-button");
  const accessToken = localStorage.getItem("access_token");
  const services = document.getElementById("services");
  const aboutUs = document.getElementById("about-us");
  const blog = document.getElementById("blog");
  const testimonials = document.getElementById("testimonials");
  const unwantedItems = document.getElementById("unwanted");
  const contactUs = document.getElementById("contact");
  const ourTeam = document.getElementById("our-team");
  const getStartedBtn = document.getElementById("get-started-btn");

  if (accessToken) {
    // User has a valid access token
    contactUs.textContent = "Subscriptions";
    contactUs.setAttribute("href", "/subscriptions");

    contactUs.setAttribute("href", "/subscriptions");
    unwantedItems.style.display = "none";
    blog.style.display = "none";
    aboutUs.textContent = "My Bussiness";
    aboutUs.setAttribute("href", "/my-business");
    ourTeam.textContent = "Boost My Bussiness";
    ourTeam.setAttribute("href", "/boost-my-business");
    testimonials.setAttribute("href", "/boost-my-business");
    loginButton.textContent = "Logout";
    loginButton.setAttribute("href", "/");
    getStartedBtn.textContent = "My Insights";
    getStartedBtn.setAttribute("href", "/insights");
  }

  loginButton.addEventListener("click", function () {
    if (loginButton.textContent === "Logout") {
      window.location.href = "{{ url_for('webhook.home') }}";
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_name");
    } else {
      window.location.href = "login";
    }
  });

  function sendRequest(method, url, data) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader("Authorization", "Bearer " + accessToken);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          console.log(response);
        } else {
          console.error("Request failed with status:", xhr.status);
        }
      }
    };
    xhr.send(JSON.stringify(data));
  }
});
