function validateAndSubmit() {
    let first_name = document.getElementById('firstname').value.trim().split(' ').join('');
    let last_name = document.getElementById('lastname').value.trim().split(' ').join('');
    let college_name = document.getElementById('collegename').value.trim();
    let email_id = document.getElementById('email').value.trim().split(' ').join('');
    let password1 = document.getElementById('password1').value.trim().split(' ').join('');
    let password2 = document.getElementById('password2').value.trim().split(' ').join('');
    let phone_no = document.getElementById('phoneno').value.trim().split(' ').join('');
    let card_no = document.getElementById('cardnumber').value.trim().split(' ').join('');
    let card_cvv = document.getElementById('cardcvv').value.trim().split(' ').join('');
    let plan_subscribed = document.getElementById('plan').innerText.trim();

    if (first_name === '') {
        displayFormErrorMessage('First name can not be empty. Please enter a valid first name.');
    } else if (hasNumber(first_name)) {
        displayFormErrorMessage('First name can not contain numbers. Please enter a valid first name.');
    } else if (last_name === '') {
        displayFormErrorMessage('Last name can can not be empty. Please enter a valid last name.');
    } else if (hasNumber(last_name)) {
        displayFormErrorMessage('Last name can not contain numbers. Please enter a valid last name.');
    } else if (email_id === '') {
        displayFormErrorMessage('Email id can not be empty. Please enter a valid email id.');
    } else if (checkEmailInvalid(email_id)) {
        displayFormErrorMessage('Email id is invalid. Please enter a valid email id.');
    } else if (password1 === '') {
        displayFormErrorMessage('The password that you have entered is invalid. ' +
            'Please enter a valid password.');
    } else if (password1 !== password2) {
        displayFormErrorMessage('Password mismatch. Please make sure that both passwords are same.');
    } else if (password1.length < 8 || password1.length > 16) {
        displayFormErrorMessage('Password should be between 8 and 16 characters long');
    } else if (checkPhoneInvalid(phone_no.trim())) {
        displayFormErrorMessage('The phone number you have entered is invalid. ' +
            'Please enter a valid phone number.');
    } else if (checkCardInvalid(card_no.trim()) || checkCardInvalid(card_cvv.trim()) ||
        card_no.trim().length < 16 || card_cvv.trim().length < 3) {
        displayFormErrorMessage('The credit/debit card number or the CVV number that you have entered ' +
            'is invalid. Please check the number and try again.');
    } else if (card_no.trim() === '') {
        displayFormErrorMessage('The credit/debit card number that you have entered is invalid.');
    } else if (card_cvv.trim() === '') {
        displayFormErrorMessage('The CVV number that you have entered is invalid.');
    } else {
        // all the form data is submittable
        // so we do an AJAX call to 'signup/<str:plan_subscribed>'
        let url = '/signup/' + plan_subscribed;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'first_name': first_name,
                'last_name': last_name,
                'college_name': college_name,
                'email_id': email_id,
                'password': password1,
                'phone_no': phone_no,
                'card_no': card_no,
                'card_cvv': card_cvv,
                'plan_subscribed': plan_subscribed,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'failed') {
                displayFormErrorMessage('Server error! ' + data['msg']);
            } else {
                location.replace('/college/');
            }
        });
    }

}

function hasNumber(myString) {
    // Returns true if the string has a number otherwise returns false.
    return /\d/.test(myString);
}

function checkEmailInvalid(emailId) {
    /*
    There are many criteria that need to be follow to validate the email id such as:
    * email id must contain the @ and . character
    * There must be at least one character before and after the @.
    * There must be at least two characters after . (dot).
     */
    let atSymbolPosition = emailId.indexOf('@');
    let dotSymbolPosition = emailId.indexOf('.');
    return atSymbolPosition < 1 || dotSymbolPosition < (atSymbolPosition + 2) || (dotSymbolPosition + 2) >= emailId.length;

}

function checkPhoneInvalid(phoneNum) {
    return !(phoneNum.match(/^\+?([0-9]{2})\)?[-. ]?([0-9]{5})[-. ]?([0-9]{5})$/) && phoneNum.length <= 13);

}

function checkCardInvalid(cardNum) {
    return !cardNum.match(/^[0-9]+$/);

}

function displayFormErrorMessage(errorMessage) {
    $('#formerror').show();
    $('#alertmessage').text(errorMessage);
}


// jQuery codes
// jQuery code for closing the bootstrap-alert when the 'x' button is clicked
$(document).ready(function () {
    $('#alertclose').click(function () {
        $('#formerror').hide();
    });
});

// jQuery for formatting card number field with spaces after every 4 digits.
// for e.g. 1234567891234567 will be formatted as 1234 5678 9123 4567
// This is just for increasing the readability for the user.
$(document).ready(function () {
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
});

// For enabling bootstrap tooltip
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});
