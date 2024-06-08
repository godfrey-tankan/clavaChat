document.addEventListener("DOMContentLoaded", function () {
  const loginButton = document.getElementById("login-button");
  const accessToken = localStorage.getItem("access_token");
  const services = document.getElementById("services");
  const aboutUs = document.getElementById("about-us");
  const blog = document.getElementById("blog");
  const testimonials = document.getElementById("testimonials");
  const unwantedItems = document.getElementById("unwanted");
  const contactUs = document.getElementById("contact");
  const getStartedBtn = document.getElementById("get-started-btn");
  const mobileLoginIcon = document.getElementById("arrow-login");
  const analyticsBtn = document.getElementById("analyze");

  if (accessToken) {
    // User has a valid access token
    try {
      loginButton.textContent = "Logout";
      loginButton.setAttribute("href", "/");
      getStartedBtn.textContent = "My Insights";
      getStartedBtn.setAttribute("href", "/insights");
      contactUs.textContent = "Subscriptions";
      contactUs.setAttribute("href", "/subscriptions");
      contactUs.setAttribute("href", "/subscriptions");
      unwantedItems.style.display = "none";
      mobileLoginIcon.style.display = "none";
      blog.style.display = "none";
      aboutUs.textContent = "My Bussiness";
      aboutUs.setAttribute("href", "/my-business");
      testimonials.setAttribute("href", "/boost-my-business");
    } catch (e) {
      // console.log(e);
    }
  }

  loginButton.addEventListener("click", function () {
    window.location.href = "{{ url_for('webhook.home') }}";
    if (loginButton.textContent === "Logout") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_name");
    } else {
      window.location.href = "login";
    }
  });

  // analytics && insights section
  analyticsBtn.addEventListener("click", function () {
    $.ajax({
      url: "/insights",
      contentType: "application/json",
      method: "POST",
      data: JSON.stringify({
        access_token: accessToken,
        user_name: localStorage.getItem("user_name"),
      }),
      success: function (response) {
        // Update the subscription plan details in the HTML elements
        $("#searcher").text(response.searcher);
        $("#product").text(response.product);
        console.log("response:", response);
        if (response.error) {
          // Change the context of the "Upgrade Plan" button to "Change Plan"
          $("#erorr").text(response.error);
        }
        // Update other subscription plan details as needed
      },
    });
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
