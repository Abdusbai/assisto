const menuButton = document.querySelector(".menuButton_Container");
const arrow = document.querySelectorAll(".arrow");

// Function to close all sub-menus
function CloseAllSubs() {
    for (let j = 0; j < arrow.length; j++) {
        if (arrow[j].querySelector(".sub-menu").classList.contains("open_sub")) {
            arrow[j].querySelector(".sub-menu").classList.remove("open_sub");
            arrow[j].querySelector(".group__icon").classList.remove("rotate");
        }
    }
}

// Event listener for menu button click
if (menuButton) {
    menuButton.addEventListener("click", function () {
        document.querySelector(".body__container").classList.toggle("close_menu");
        this.classList.toggle("menu_clicked");
        CloseAllSubs();
    });
}

// Event listeners for arrow clicks
if (arrow) {
    for (let i = 0; i < arrow.length; i++) {
        arrow[i].addEventListener("click", function () {
            arrow[i].querySelector(".sub-menu").classList.toggle("open_sub");
            arrow[i].querySelector(".group__icon").classList.toggle("rotate");

            for (let j = 0; j < arrow.length; j++) {
                if (arrow[j] === this) {
                    continue
                } else {
                    if (
                        arrow[j].querySelector(".sub-menu").classList.contains("open_sub")
                    ) {
                        arrow[j].querySelector(".sub-menu").classList.remove("open_sub");
                        arrow[j].querySelector(".group__icon").classList.remove("rotate");
                    }
                }
            }
        });
    }
}

// Character counter for textarea
const textarea = document.getElementById('myTextarea');
const charRemaining = document.getElementById('charRemaining');

if (textarea) {
    textarea.addEventListener('input', function () {
        const maxLength = 200;
        const currentLength = textarea.value.length;
        const remaining = maxLength - currentLength;

        charRemaining.textContent = remaining;

        textarea.addEventListener('keydown', function (event) {
            let inputValue = this.value;

            if (inputValue.length >= maxLength && event.key !== 'Backspace') {
                event.preventDefault();
            }
        });
    });
}


// Retrieve the accepter button and textarea element
const accepterBtn = document.getElementById('accepterBtn');
const refuserBtn = document.getElementById('refuserBtn');
const text_area = document.getElementById('msg-area');

// Add event listener to the accepter button
if (accepterBtn && refuserBtn) {
    accepterBtn.addEventListener('click', function (event) {
        // Get the textarea text
        const textareaText = text_area.value;

        // Get the original accepter URL
        const originalUrl = accepterBtn.href;

        // Construct the modified accepter URL with the textarea text as a query parameter
        const modifiedUrl = originalUrl + '?message=' + encodeURIComponent(textareaText);

        // Update the href attribute of the accepter button with the modified URL
        accepterBtn.href = modifiedUrl;
    });

    refuserBtn.addEventListener('click', function (event) {
        // Get the textarea text
        const textareaText = text_area.value;

        // Get the original refuser URL
        const originalUrl = refuserBtn.href;

        // Construct the modified refuser URL with the textarea text as a query parameter
        const modifiedUrl = originalUrl + '?message=' + encodeURIComponent(textareaText);

        // Update the href attribute of the refuser button with the modified URL
        refuserBtn.href = modifiedUrl;
    });
}


function showSuccessMessage() {
    const successMessage = document.querySelector('.messages');
    if (successMessage) {
        successMessage.style.opacity = '1';
        setTimeout(function () {
            successMessage.style.opacity = '0';
        }, 3000); // Adjust the timeout duration (in milliseconds) as needed
    }
}

// Call the function when the page loads
window.addEventListener('load', showSuccessMessage);

const yearElement = document.getElementById("year"); // Select the element with ID "year"
if (yearElement) {
    yearElement.innerHTML = new Date().getFullYear(); // Set the inner HTML of the yearElement to the current year
}