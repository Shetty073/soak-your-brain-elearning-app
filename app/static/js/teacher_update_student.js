function validateAndUpdateStudent() {
    let first_name = document.getElementById('firstname').value.trim().split(' ').join('');
    let last_name = document.getElementById('lastname').value.trim().split(' ').join('');
    let class_assigned = $('#selectclasses').val();
    let email_id = document.getElementById('email').value.trim().split(' ').join('');
    let password1 = document.getElementById('password1').value.trim().split(' ').join('');
    let password2 = document.getElementById('password2').value.trim().split(' ').join('');

    if (first_name === '') {
        displayFormErrorMessage(false,
            'First name can not be empty. Please enter a valid first name.', 'alertmessage');
    } else if (hasNumber(first_name)) {
        displayFormErrorMessage(false,
            'First name can not contain numbers. Please enter a valid first name.', 'alertmessage');
    } else if (last_name === '') {
        displayFormErrorMessage(false,
            'Last name can can not be empty. Please enter a valid last name.', 'alertmessage');
    } else if (hasNumber(last_name)) {
        displayFormErrorMessage(false,
            'Last name can not contain numbers. Please enter a valid last name.', 'alertmessage');
    } else if (email_id === '') {
        displayFormErrorMessage(false,
            'Email id can not be empty. Please enter a valid email id.', 'alertmessage');
    } else if (checkEmailInvalid(email_id)) {
        displayFormErrorMessage(false,
            'Email id is invalid. Please enter a valid email id.', 'alertmessage');
    } else if (password1 !== '' && password1 !== password2) {
        displayFormErrorMessage(false,
            'Password mismatch. Please make sure that both passwords are same.', 'alertmessage');
    } else if ((password1 !== '') && (password1.length < 8 || password1.length > 16)) {
        displayFormErrorMessage(false,
            'Password should be between 8 and 16 characters long', 'alertmessage');
    } else if (class_assigned === '' || class_assigned === null) {
        displayFormErrorMessage(false,
            'You must assign this teacher to at least one class', 'alertmessage');
    } else {
        let url = window.location.href;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'mode': 'update',
                'first_name': first_name,
                'last_name': last_name,
                'class_assigned': class_assigned,
                'email_id': email_id,
                'password1': password1,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'success') {
                window.location.replace('/college/teacher/view_student_lists');
            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });
    }
}