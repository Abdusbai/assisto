$(document).ready(function () {
    $('#textInput').on('keydown', function (event) {
        let inputValue = $(this).val();
        let maxLength = 240;

        if (inputValue.length >= maxLength && event.key !== 'Backspace') {
            event.preventDefault();
        }
    });

    $(window).on('load', scrollToBottom);

    const main = $('main');
    const scrollDownButton = $('.scroll-down-button');

    if (main.length && scrollDownButton.length) {
        main.on('scroll', function () {
            if (Math.ceil(main.scrollTop()) + 1 < main[0].scrollHeight - main[0].clientHeight) {
                scrollDownButton.addClass('show');
            } else {
                scrollDownButton.removeClass('show');
            }
        });

        scrollDownButton.on('click', function (event) {
            event.preventDefault();
            main.animate({
                scrollTop: main[0].scrollHeight - main[0].clientHeight
            }, 'slow');
        });
    }

    const documentHeight = () => {
        const doc = document.documentElement;
        doc.style.setProperty('--doc-height', `${window.innerHeight}px`);
    };

    $(window).on('resize', documentHeight);
    documentHeight();

    const btn_dark_light = $('.btn-dark-light');
    const body = $('body');

    if (btn_dark_light.length) {
        btn_dark_light.on('click', function (e) {
            e.preventDefault();
            btn_dark_light.toggleClass('onoff');
            body.toggleClass('dark-mode');
        });
    }

    setInitialMessage();

    $('#textInput').keypress(function (event) {
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
                url: "/getResponse",
                method: 'POST',
                processData: false,
                contentType: false,
                mimeType: "multipart/form-data",
                data: formData,
                success: function (response) {
                    const responseObject = JSON.parse(response); //Parse the response string into a JavaScript object.
                    let fileUrl = responseObject.file_url;
                    let file_size = responseObject.file_size;
                    let file_name = responseObject.file_name;
                    let file_number = responseObject.file_number;
                    let step = responseObject.step;
                    let maxLength = 25; // Maximum length of the file name
                    let truncatedFileName = file_name.length > maxLength ? file_name.substr(0, maxLength) + '....pdf' : file_name;
                    const date = new Date();
                    const userHTML =
                        "<div class=\"msg user-msg\"> " +
                        "<span class=\"file-download\">" +
                        "<img src=\"static/assisto/img/pdf.png\" alt=\"pdf logo\" class=\"pdf-logo\">" +
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


                    const botHTML =
                        "<div class='msg boot-msg'>" +
                        "<p>" +
                        "<span class='mb'>Veuillez choisir votre <strong>type de profession</strong> :</span>" +
                        "<strong>1:</strong> Agriculteur<br>" +
                        "<strong>2:</strong> Eleveur<br>" +
                        "<strong>3:</strong> Apiculteur" +
                        "</p>" +
                        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
                        "</div>";


                    const botLastHtml =
                        "<div class='msg boot-msg'>" +
                        "<p>Votre demande sera examinée dans les plus brefs délais, merci</p>" +
                        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
                        "</div>";


                    setTimeout(function () {
                        $('#chatbot').append(userHTML);
                        $('#textInput').prop('disabled', false);
                        $('#fileInput').prop('disabled', true);
                        $('#textInput').focus();
                        scrollToBottom()
                        setTimeout(function () {
                            if (parseInt(file_number) === 2) {
                                $('#chatbot').append(botLastHtml);
                                $('#textInput').prop('disabled', true);
                            } else {
                                $('#chatbot').append(botHTML);
                            }
                            scrollToBottom()
                        }, 500)

                    }, 500)
                },
                error: function (xhr, status, error) {
                }
            });
        } else {
            const date = new Date();
            const botHTML =
                "<div class='msg boot-msg'> " +
                "<p>Type de fichier invalide. Veuillez choisir un fichier au format PDF</p> " +
                "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                "</div>";

            $('#chatbot').append(botHTML);
            setTimeout(function () {
                scrollToBottom()
                $('#textInput').prop('disabled', false);
                $('#textInput').focus();
            }, 500)
        }
        $("#fileInput").val("");
    });
});


let userStep = 0;
$('#textInput').prop('disabled', true);
$('#fileInput').prop('disabled', true);

function getUserResponse() {
    const userText = $('#textInput').val();

    if (userText !== "") {
        const date = new Date();
        const userHTML =
            "<div class='msg user-msg'> " +
            "<p>" + userText.toUpperCase() + "</p> " +
            "<span class='user-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
            "</div>";
        $('#textInput').val("");
        $('#textInput').prop('disabled', true);
        $('#chatbot').append(userHTML);
        scrollToBottom()


        $.get('/getResponse', {
            userMessage: userText,
            stepMessage: userStep
        }).done(function (response) {
            $(".status").text("Entrain d'écrire .....")
            setTimeout(function () {
                if (response.upload_file) {
                    $('#fileInput').prop('disabled', false);
                    $('#textInput').prop('disabled', true);
                } else {
                    $('#textInput').prop('disabled', false);
                }
                if (response.try_again) {
                    location.reload();
                } else {
                    if (response.response !== '') {
                        if (response.att) {
                            const botHTML =
                                "<div class='msg boot-msg'> " +
                                response.response +
                                "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                                "</div>";
                            $('#chatbot').append(botHTML);
                            $('#textInput').prop('disabled', true);
                        } else {
                            const botHTML =
                                "<div class='msg boot-msg'> " +
                                "<p>" + response.response + "</p> " +
                                "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                                "</div>";
                            $('#chatbot').append(botHTML);
                        }

                        userStep = response.step
                    }
                    if (response.again !== '') {
                        const again_msg =
                            "<div class='msg boot-msg'> " +
                            "<p>" + response.again + "</p> " +
                            "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
                            "</div>";
                        $('#chatbot').append(again_msg);
                    }
                }
                scrollToBottom()
                $('#textInput').focus();
                $(".status").text("En ligne")
            }, 500)
        })
    }

}

function setInitialMessage() {
    const date = new Date();

    const initialBotHTML =
        "<div class='msg boot-msg'> " +
        "<p>Bonjour ! Bienvenue sur Assisto, le chatbot de la Chambre d'Agriculture de la Région de l'Oriental</p> " +
        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span> " +
        "</div>";
    $('#chatbot').append(initialBotHTML);

    const firstMsg =
        "<div class='msg boot-msg'>" +
        "<p>" +
        "<span class='mb'>Êtes-vous :</span>" +
        "<strong>1:</strong> Particulier<br>" +
        "<strong>2:</strong> Coopérative<br>" +
        "<strong>3:</strong> Société" +
        "</p>" +
        "<span class='boot-date'>" + String(date.getHours()).padStart(2, '0') + ':' + String(date.getMinutes()).padStart(2, '0') + "</span>" +
        "</div>";
    $('#chatbot').append(firstMsg);
    $('#textInput').prop('disabled', false);
    $('#textInput').focus();
}

function scrollToBottom() {
    let main = $('main');
    main.scrollTop(main[0].scrollHeight);
}


$('#button-input').click(function () {
    getUserResponse();
})


