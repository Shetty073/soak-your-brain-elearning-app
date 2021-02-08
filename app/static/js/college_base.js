function validateAndAddDepartment(addMore) {
    let url = "/college/add_classes";
    let departmentName = document.getElementById('deptname').value.trim()
    if (checkNameInvalid(departmentName)) {
        displayFormErrorMessage(false, 'Department names cannot contain special characters except _',
            'deptalertmessage');
    } else if (departmentName === '') {
        displayFormErrorMessage(false, 'Please enter a valid department name.',
            'deptalertmessage');
    } else {
        // Send the data via AJAX and be on the same page
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'form_type': 'department',
                'department_name': departmentName,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'success') {
                // Request successfully completed. Clear the input box
                document.getElementById('deptname').value = '';
                displayFormErrorMessage(true, data['msg'], 'deptalertmessage');
                if (addMore === false) {
                    // Go to home page
                    window.location.replace('/college/');
                }

                // Update departments dropdown list
                $('#selectdepartment').append(new Option(departmentName, departmentName));

            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'deptalertmessage');
            }
        });
    }
}

function validateAndAddClass(addMore) {
    let url = "/college/add_classes";
    let className = document.getElementById('classname').value.trim();
    let departmentName = document.getElementById('selectdepartment').value.trim();
    if (checkNameInvalid(className) || checkNameInvalid(departmentName)) {
        displayFormErrorMessage(false, 'Class and department names cannot contain special characters ' +
            'except _', 'clsalertmessage');
    } else if (className === '' || departmentName === '') {
        displayFormErrorMessage(false, 'Please enter a valid class/department name.',
            'clsalertmessage');
    } else {
        // Send the data via AJAX and be on the same page
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'form_type': 'class',
                'class_name': className,
                'department_name': departmentName,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'success') {
                // Request successfully completed. Clear the input box
                document.getElementById('classname').value = '';
                displayFormErrorMessage(true, data['msg'], 'clsalertmessage');
                if (addMore === false) {
                    // Go to home page
                    window.location.replace('/college/');
                }
            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'clsalertmessage');
            }
        });
    }
}

function validateAndAddTeacher(addMore) {
    let url = "/college/add_teachers";

    let first_name = document.getElementById('firstname').value.trim().split(' ').join('');
    let last_name = document.getElementById('lastname').value.trim().split(' ').join('');
    let email_id = document.getElementById('email').value.trim().split(' ').join('');
    let password1 = document.getElementById('password1').value.trim().split(' ').join('');
    let password2 = document.getElementById('password2').value.trim().split(' ').join('');

    // Get the multiple <select> values
    let classes_assigned = $('#selectclasses').val();

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
    } else if (password1 === '') {
        displayFormErrorMessage(false,
            'The password that you have entered is invalid. Please enter a valid password.',
            'alertmessage');
    } else if (password1 !== password2) {
        displayFormErrorMessage(false,
            'Password mismatch. Please make sure that both passwords are same.', 'alertmessage');
    } else if (password1.length < 8 || password1.length > 16) {
        displayFormErrorMessage(false,
            'Password should be between 8 and 16 characters long', 'alertmessage');
    } else if (classes_assigned.length < 1) {
        displayFormErrorMessage(false,
            'You must assign this teacher to at least one class', 'alertmessage');
    } else {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'mode': 'add',
                'first_name': first_name,
                'last_name': last_name,
                'classes_assigned': classes_assigned,
                'email_id': email_id,
                'password1': password1,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'success') {
                // Request successfully completed. Clear the input box
                document.getElementById('firstname').value = '';
                document.getElementById('lastname').value = '';
                $('#selectclasses').val('')
                document.getElementById('email').value = '';
                document.getElementById('password1').value = '';
                document.getElementById('password2').value = '';
                displayFormErrorMessage(true, data['msg'], 'alertmessage');
                if (addMore === false) {
                    // Go to home page
                    window.location.replace('/college/');
                }
            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });
    }
}

function checkNameInvalid(departmentName) {
    return !!departmentName.split(' ').join('').match(/\W/g);

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
    if (atSymbolPosition < 1 || dotSymbolPosition < (atSymbolPosition + 2) || (dotSymbolPosition + 2) >= emailId.length) {
        return true;
    }
    return false;
}

function displayFormErrorMessage(success, errorMessage, msgFieldId) {
    let dict = {
        'deptalertmessage': 'deptformerror',
        'clsalertmessage': 'clsformerror',
        'alertmessage': 'formerror',
        'subjectalertmessage': 'subjectformerror',
        'clssubjectalertmessage': 'clssubjectformerror',
    };
    if (success === true) {
        // This is a success message
        if (document.getElementById(dict[msgFieldId]).classList.contains('alert-warning')) {
            document.getElementById(dict[msgFieldId]).classList.remove('alert-warning');
            if (!document.getElementById(dict[msgFieldId]).classList.contains('alert-success')) {
                document.getElementById(dict[msgFieldId]).classList.add('alert-success');
            }
        }
    } else if (success === false) {
        // This is an error message
        if (document.getElementById(dict[msgFieldId]).classList.contains('alert-success')) {
            document.getElementById(dict[msgFieldId]).classList.remove('alert-success');
            if (!document.getElementById(dict[msgFieldId]).classList.contains('alert-warning')) {
                document.getElementById(dict[msgFieldId]).classList.add('alert-warning');
            }
        }
    }
    let errorBlock = document.getElementById(msgFieldId);
    errorBlock.innerText = errorMessage;
    let errorAlert = document.getElementById(msgFieldId);
    document.getElementById(dict[msgFieldId]).style.display = 'block';
}

// jQuery section
// jQuery code for closing the bootstrap-alert when the 'x' button is clicked
$(document).ready(function () {
    $('#deptalertclose').click(function () {
        $('#deptformerror').css('display', 'none');
    });
    $('#clsalertclose').click(function () {
        $('#clsformerror').css('display', 'none');
    });
    $('#alertclose').click(function () {
        $('#formerror').css('display', 'none');
    });
});

$(document).ready(function () {
    // For bootstrap tooltip
    $('[data-toggle="tooltip"]').tooltip();

    // For displaying selected file's name
    $('input[type=file]').change(function(e){
        $(this).prev()[0].innerText = `Selected: ${$(this)[0].files[0].name}`;
    });
});
