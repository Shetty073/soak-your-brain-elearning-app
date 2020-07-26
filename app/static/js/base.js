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
    } else if (password1.length < 8 && password1.length > 16) {
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
                'X-CSRFToken': csrftoken
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
                displayFormErrorMessage('Server error!' + data['error']);
            }
        });
    }

}

function hasNumber(myString) {
    // Returns true if the string has a number otherwise returns false.
    return /\d/.test(myString);
}

function checkEmailInvalid(email_id) {
    /*
    There are many criteria that need to be follow to validate the email id such as:
    * email id must contain the @ and . character
    * There must be at least one character before and after the @.
    * There must be at least two characters after . (dot).
     */
    let atSymbolPosition = email_id.indexOf('@');
    let dotSymbolPosition = email_id.indexOf('.');
    if (atSymbolPosition < 1 || dotSymbolPosition < (atSymbolPosition + 2) || (dotSymbolPosition + 2) >= email_id.length) {
        return true;
    }
    return false;
}

function checkPhoneInvalid(phone_num) {
    if (phone_num.match(/^\+?([0-9]{2})\)?[-. ]?([0-9]{5})[-. ]?([0-9]{5})$/) && phone_num.length <= 13) {
        return false;
    }
    return true;
}

function checkCardInvalid(card_num) {
    if (card_num.match(/^[0-9]+$/)) {
        return false;
    }
    return true;
}

function displayFormErrorMessage(errorMessage) {
    let errorBlock = document.getElementById('alertmessage');
    errorBlock.innerText = errorMessage;
    let errorAlert = document.getElementById('formerror');
    errorAlert.style.display = 'block';
}


// jQuery codes
$('#alertclose').click(function () {
    $('#formerror').css('display', 'none');
});

// jQuery for formatting card number field with spaces after every 4 digits.
// for e.g. 1234567891234567 will be formatted as 1234 5678 9123 4567
// This is just for increasing the readability for the user.
$(document).ready(function () {
    $("#cardnumber").keydown(function (e) {
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
