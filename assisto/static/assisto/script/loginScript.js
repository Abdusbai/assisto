const buttonSHowHide = document.querySelector(".btn-showPassword"); // Select the element with class "btn-showPassword"
const PasswordInput = document.getElementsByName("password")[0]; // Select the first element with the name "password"

const yearElement = document.getElementById("year"); // Select the element with ID "year"
if (yearElement) {
    yearElement.innerHTML = new Date().getFullYear(); // Set the inner HTML of the yearElement to the current year
}

if (buttonSHowHide && PasswordInput) {
    buttonSHowHide.addEventListener("click", function (e) {
        e.preventDefault();
        buttonSHowHide.classList.toggle("openclose"); // Toggle the "openclose" class on buttonSHowHide element

        if (PasswordInput.type === "password") {
            PasswordInput.type = "text"; // Change the input type to "text" (show password)
        } else {
            PasswordInput.type = "password"; // Change the input type to "password" (hide password)
        }
    });
}

let loginForm = document.querySelector("#loginForm"); // Select the element with ID "loginForm"
let userEmail = document.querySelector("#userEmail"); // Select the element with ID "userEmail"
let userPassword = document.querySelector("#userPassword"); // Select the element with ID "userPassword"

if (loginForm && userEmail && userPassword) {
    userEmail.addEventListener("change", function (i) {
        userEmail_Validation(this); // Call the userEmail_Validation function passing the userEmail element
    });

    const userEmail_Validation = function (i) {
        let message = document.getElementsByClassName("message")[0]; // Select the first element with class "message"
        if (i.value.trim() === "") {
            message.innerHTML = "Please enter your email !"; // Set the inner HTML of the message element
            i.classList.add("Error"); // Add the "Error" class to the userEmail element
            return false;
        } else if (i.value.trim().length > 100) {
            message.innerHTML = "Your email is too long !";
            i.classList.add("Error");
            return false;
        } else if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(i.value.trim()) === false) {
            message.innerHTML = "Please enter a valid Email Address !";
            i.classList.add("Error");
            return false
        } else {
            message.innerHTML = "&nbsp;";
            i.classList.remove("Error"); // Remove the "Error" class from the userEmail element
            return true;
        }
    };

    userPassword.addEventListener("change", function (i) {
        userPassword_Validation(this); // Call the userPassword_Validation function passing the userPassword element
    });

    const userPassword_Validation = function (i) {
        let message = document.getElementsByClassName("message")[1]; // Select the second element with class "message"
        if (i.value.trim() === "") {
            message.innerHTML = "Please enter your password !"; // Set the inner HTML of the message element
            i.classList.add("Error"); // Add the "Error" class to the userPassword element
            return false;
        } else if (i.value.trim().length > 20) {
            message.innerHTML = "Your password is too long !";
            i.classList.add("Error");
            return false;
        } else {
            message.innerHTML = "&nbsp;";
            i.classList.remove("Error"); // Remove the "Error" class from the userPassword element
            return true;
        }
    };

    loginForm.addEventListener("submit", function (e) {
        if (!userEmail_Validation(userEmail) || !userPassword_Validation(userPassword)) {
            e.preventDefault(); // Prevent form submission if validation fails
        }
    });
}

if (loginForm) {
    document.querySelectorAll(".close-btn").forEach(function (element) {
        element.addEventListener("click", function () {
            document.querySelectorAll(".alert").forEach(function (alert) {
                alert.classList.add("hide"); // Add the "hide" class to each element with class "alert"
                alert.classList.remove("show"); // Remove the "show" class from each element with class "alert"
            });
        });
    });
}

let alert_div = document.querySelector(".alert"); // Select the element with class "alert"
if (alert_div) {
    alert_div.addEventListener("animationend", function () {
        if (alert_div.classList.contains("show")) {
            setTimeout(function () {
                alert_div.classList.add("hide"); // Add the "hide" class to the alert_div element
                alert_div.classList.remove("show"); // Remove the "show" class from the alert_div element
                alert_div.classList.add("opp"); // Add the "opp" class to the alert_div element
            }, 2500);
        }
    });
}



