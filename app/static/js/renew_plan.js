$(document).ready(function () {
    $('#plan-price').text(`₹${$('#1').val()} / year`);

    $(document).on('change', '#plan-selector', function () {
        $('#plan-price').text(`₹${$(`#${$(this).val()}`).val()} / year`);
    });

    // jQuery for formatting card number field with spaces after every 4 digits.
    // for e.g. 1234567891234567 will be formatted as 1234 5678 9123 4567
    // This is just for increasing the readability for the user.
    $("#cardnumber").keydown(function (e) {
        // prevent user from entering alphabets and some other unwanted characters
        if ((e.keyCode >= 65 && e.keyCode <= 90) || (e.keyCode >= 106 && e.keyCode <= 111) || e.keyCode === 16) {
            e.preventDefault();
        }

        let key = e.keyCode || e.charCode;

        // Ignore keypress if keys are backspace or delete
        if (!(key === 8 || key === 46)) {
            if ($(this).val().length === 4 ||
                $(this).val().length === 9 ||
                $(this).val().length === 14) {
                $(this).val($(this).val() + ' ');
            }
        }
    });

    // format the autofilled card number
    let card_number = $('#cardnumber').val();
    let spaced_card_number = '';
    for (let i = 0; i < card_number.length; i++) {
        if (i % 4 === 0) {
            spaced_card_number += ' ' + card_number[i];
        } else {
            spaced_card_number += card_number[i];
        }
    }
    $('#cardnumber').val(spaced_card_number.trim());

});
