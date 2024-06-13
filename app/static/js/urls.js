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
        const tableBody = $("#insights-tbody");
        tableBody.empty(); // Clear the table body

        let loadedCount = 0;
        const maxToDisplay = 10; // Set the maximum number of items to display initially

        // Loop through the response and add the items to the table
        response.forEach((item) => {
          if (loadedCount < maxToDisplay) {
            const row = $("<tr></tr>");
            row.append($("<td></td>").text(item.searcher));
            row.append($("<td></td>").text(item.product));
            row.append($("<td></td>").text(item.error || ""));
            tableBody.append(row);
            loadedCount++;
          }
        });

        const container = $("#analysis-container");
        container.off("scroll"); // Remove any existing event listener
        container.on("scroll", function () {
          if (
            $(this).scrollTop() + $(this).innerHeight() >=
            $(this)[0].scrollHeight
          ) {
            loadMoreItems(tableBody, response, maxToDisplay, loadedCount);
          }
        });
      },
    });
  });

  function loadMoreItems(tableBody, response, maxToDisplay, loadedCount) {
    response.slice(loadedCount).forEach((item) => {
      const row = $("<tr></tr>");
      row.append($("<td></td>").text(item.searcher));
      row.append($("<td></td>").text(item.product));
      row.append($("<td></td>").text(item.error || ""));
      tableBody.append(row);
      loadedCount++;
    });
  }

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
