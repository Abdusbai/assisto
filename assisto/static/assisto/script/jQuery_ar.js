$(document).ready(function () {
    $('#textInput').on('keydown', function (event) {
        let inputValue = $(this).val();
        let maxLength = 240;

        // Prevent further input when maximum character limit is reached
        if (inputValue.length >= maxLength && event.key !== 'Backspace') {
            event.preventDefault();
        }
    });

    $(window).on('load', scrollToBottom);

    const main = $('main');
    const scrollDownButton = $('.scroll-down-button');

    if (main.length && scrollDownButton.length) {
        // Show scroll down button when not at the bottom of the scrollable area
        main.on('scroll', function () {
            if (Math.ceil(main.scrollTop()) + 1 < main[0].scrollHeight - main[0].clientHeight) {
                scrollDownButton.addClass('show');
            } else {
                scrollDownButton.removeClass('show');
            }
        });

        // Scroll to the bottom when scroll down button is clicked
        scrollDownButton.on('click', function (event) {
            event.preventDefault();
            main.animate({
                scrollTop: main[0].scrollHeight - main[0].clientHeight
            }, 'slow');
        });
    }

    // Set document height for CSS styling
    const documentHeight = () => {
        const doc = document.documentElement;
        doc.style.setProperty('--doc-height', `${window.innerHeight}px`);
    };

    $(window).on('resize', documentHeight);
    documentHeight();

    const btn_dark_light = $('.btn-dark-light');
    const body = $('body');

    if (btn_dark_light.length) {
        // Toggle dark mode
        btn_dark_light.on('click', function (e) {
            e.preventDefault();
            btn_dark_light.toggleClass('onoff');
            body.toggleClass('dark-mode');
        });
    }

    setInitialMessage();

    $('#textInput').keypress(function (event) {
        // Submit user input when Enter key is pressed
        if (event.which === 13) {
            event.preventDefault();
            $('.Sd').click();
        }
    });

    $('#fileInput').on('change', function () {
        const file = $('#fileInput')[0].files[0];
        const validExtensions = ['pdf'];

        if (file && validExtensions.includes(file.name.split('.').pop().toLowerCase())) {
            const csrfToken = $('[name="csrfmiddlewaretoken"]').val();
            const formData = new FormData();
            formData.append('file', file);
            formData.append('csrfmiddlewaretoken', csrfToken);

            $.ajax({
                url: "/getResponse", // URL to send the AJAX request
                method: 'POST', // HTTP method for the request
                processData: false, // Indicates that the data should not be processed
                contentType: false, // Indicates that the content type should not be set automatically
                mimeType: "multipart/form-data", // MIME type of the data being sent
                data: formData, // The data to send in the request
                success: function (response) {
                    const responseObject = JSON.parse(response); //Parse the response string into a JavaScript object.
                    let fileUrl = responseObject.file_url; // Get the file URL from the response
                    let file_size = responseObject.file_size; // Get the file size from the response
                    let file_name = responseObject.file_name; // Get the file name from the response
                    let file_number = responseObject.file_number; // Get the file number from the response
                    let step = responseObject.step; // Get the step from the response
                    let maxLength = 25; // Maximum length of the file name
                    let truncatedFileName = file_name.length > maxLength ? file_name.substr(0, maxLength) + '....pdf' : file_name; // Truncate the file name if it exceeds the maximum length
                    const date = new Date();

                    // Construct the user's HTML message with the file information
                    const userHTML =
                        "<div class=\"msg user-msg\"> " +
                        "<span class=\"file-download\">" +
                        "<img src=\"../static/assisto/img/pdf.png\" alt=\"pdf logo\" class=\"pdf-logo\">" +
                        "<span class=\"file-infos\">" +
                        "<p class=\"file-name\" title=\"" + file_name + "\">" + truncatedFileName + "</p>" +
                        "<p> <span class=\"file-size\">" + file_size + "</span> </p>" +
                        "</span>" +
                        "<a href=\"" + staticURL + fileUrl + "\" class=\"download-link\">" +
                        "<svg xmlns='http://www.w3.org/2000/svg' class='download-logo' viewBox='0 0 512 512'>" +
                        "<path fill='none' stroke='currentColor' stroke-linecap='round' stroke-linejoin='round' stroke-width='32' d='M176 262.62L256 342l80-79.38M256 330.97V170' />" +
                        "<path d='M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64z' fill='none' stroke='currentColor' stroke-miterlimit='10' />" +
                        "</svg>" +
                        "</a>" +
                        "</span>" +
                        "<span class='user-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                        "</div>"

                    // Construct the bot's HTML response
                    const botHTML =
                        "<div class='msg boot-msg'>" +
                        "<p>" +
                        "<span class='mb'>يرجى اختيار نوع مهنتك :</span>" +
                        "<strong>1:</strong> فلاح<br>" +
                        "<strong>2:</strong> مربي الماشية<br>" +
                        "<strong>3:</strong> مربي النحل" +
                        "</p>" +
                        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
                        "</div>";


                    const botLastHtml =
                        "<div class='msg boot-msg'>" +
                        "<p>سيتم دراسة طلبكم في أقرب وقت ممكن. شكرًا</p>" +
                        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
                        "</div>";


                    setTimeout(function () {
                        // Start of setTimeout block
                        $('#chatbot').append(userHTML); // Append userHTML to #chatbot element
                        $('#textInput').prop('disabled', false); // Enable text input
                        $('#fileInput').prop('disabled', true); // Disable file input
                        $('#textInput').focus(); // Set focus on the text input field
                        scrollToBottom(); // Scroll to the bottom of the chat window
                        setTimeout(function () {
                            // Start of nested setTimeout block
                            if (parseInt(file_number) === 2) {
                                $('#chatbot').append(botLastHtml); // Append botLastHtml to #chatbot element
                                $('#textInput').prop('disabled', true); // Disable text input
                            } else {
                                $('#chatbot').append(botHTML); // Append botHTML to #chatbot element
                            }
                            scrollToBottom(); // Scroll to the bottom of the chat window
                        }, 500); // Delay of 500 milliseconds for the nested setTimeout block

                    }, 500); // Delay of 500 milliseconds for the outer setTimeout block
                },
                error: function (xhr, status, error) {
                }
            });
        } else {
            const date = new Date(); // Create a new Date object
            const botHTML =
                "<div class='msg boot-msg'> " +
                "<p>نوع الملف غير صالح. يرجى اختيار ملف بصيغة PDF</p> " +
                "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                "</div>"; // HTML markup for displaying an error message

            $('#chatbot').append(botHTML); // Append the error message to the #chatbot element
            setTimeout(function () {
                scrollToBottom() // Scroll to the bottom of the chat window
                $('#textInput').prop('disabled', false); // Enable text input
                $('#textInput').focus(); // Set focus on the text input field
            }, 500); // Delay of 500 milliseconds before executing the setTimeout block
        }
        $("#fileInput").val(""); // Clear the value of the file input field
    });
});


let userStep = 0; // Initialize userStep variable with value 0
$('#textInput').prop('disabled', true); // Disable the text input field
$('#fileInput').prop('disabled', true); // Disable the file input field

function getUserResponse() {
    const userText = $('#textInput').val();  // Get the value of the text input field

    if (userText !== "") { // Check if the user input is not empty
        const date = new Date(); // Create a new Date object
        const userHTML =
            "<div class='msg user-msg'> " +
            "<p>" + userText.toUpperCase() + "</p> " +
            "<span class='user-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
            "</div>"; // HTML markup for displaying the user's message
        $('#textInput').val(""); // Clear the value of the text input field
        $('#textInput').prop('disabled', true); // Disable the text input field
        $('#chatbot').append(userHTML); // Append the user's message to the chat interface
        scrollToBottom(); // Scroll to the bottom of the chat window


        $.get('/getResponse', {
            userMessage: userText,
            stepMessage: userStep,
            lang: 'ar'
        }).done(function (response) {
            $(".status").text("يكتب .....") // Update the status to indicate typing
            setTimeout(function () {
                if (response.upload_file) {
                    $('#fileInput').prop('disabled', false); // Enable the file input field
                    $('#textInput').prop('disabled', true);  // Disable the text input field
                } else {
                    $('#textInput').prop('disabled', false); // Enable the text input field
                }
                if (response.try_again) {
                    location.reload(); // Reload the page
                } else {
                    if (response.response !== '') {
                        const botHTML =
                            "<div class='msg boot-msg'> " +
                            "<p>" + response.response + "</p> " +
                            "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                            "</div>"; // HTML markup for displaying the bot's response
                        $('#chatbot').append(botHTML); // Append the bot's response to the chat interface
                        userStep = response.step; // Update the user's step
                    }
                    if (response.again !== '') {
                        const again_msg =
                            "<div class='msg boot-msg'> " +
                            "<p>" + response.again + "</p> " +
                            "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                            "</div>"; // HTML markup for displaying additional bot message
                        $('#chatbot').append(again_msg); // Append the additional bot message to the chat interface
                    }
                }
                scrollToBottom() // Scroll to the bottom of the chat window
                $('#textInput').focus(); // Set focus on the text input field
                $(".status").text("متصل") // Update the status to indicate connected
            }, 500); // Delay of 500 milliseconds before executing the setTimeout block
        });
    }
}

function setInitialMessage() {
    const date = new Date(); // Create a new Date object

    const initialBotHTML =
        "<div class='msg boot-msg'> " +
        "<p>مرحبًا! أهلاً بك في أسيستو، روبوت الدردشة التابع للغرفة الفلاحية لجهة الشرق</p> " +
        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
        "</div>"; // HTML markup for displaying the initial bot message
    $('#chatbot').append(initialBotHTML); // Append the initial bot message to the chat interface

    const firstMsg =
        "<div class='msg boot-msg'>" +
        "<p>" +
        "<span class='mb'>أنت :</span>" +
        "<strong>1:</strong> فلاح<br>" +
        "<strong>2:</strong> تعاونية<br>" +
        "<strong>3:</strong> شركة" +
        "</p>" +
        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
        "</div>"; // HTML markup for displaying the options for the user's role
    $('#chatbot').append(firstMsg); // Append the options message to the chat interface
    $('#textInput').prop('disabled', false); // Enable the text input field
    $('#textInput').focus(); // Set focus on the text input field
}

function scrollToBottom() {
    let main = $('main'); // Select the main element
    main.scrollTop(main[0].scrollHeight); // Scroll to the bottom of the main element
}


$('#button-input').click(function () {
    getUserResponse();
})


