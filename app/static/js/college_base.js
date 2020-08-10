function validateAndAddDepartment(addMore) {
    let url = "/college/add_classes";
    let departmentName = document.getElementById('deptname').value.trim()
    if (checkDeptNameInvalid(departmentName)) {
        displayFormErrorMessage(false, 'Department names cannot contain special characters except _',
            'deptalertmessage')
    } else if (departmentName === '') {
        displayFormErrorMessage(false, 'Please enter a valid department name.',
            'deptalertmessage')
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
                displayFormErrorMessage(true, data['msg'], 'deptalertmessage')
                if (addMore === false) {
                    // Go to home page
                    window.location.replace('/college/');
                }
                updateDepartmentsDropdown(data['departments_list']);
            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'deptalertmessage')
            }
        });
    }
}

function validateAndAddClass(addMore) {
    // TODO: Implement this
    if (addMore === true) {
        console.log('added');
    } else {
        console.log('added and back');
    }
}

function checkDeptNameInvalid(departmentName) {
    if (departmentName.split(' ').join('').match(/\W/g)) {
        return true;
    }
    return false;
}

function displayFormErrorMessage(success, errorMessage, msgFieldId) {
    let dict = {
        'deptalertmessage': 'deptformerror',
        'clsalertmessage': 'clsformerror',
    };
    if (success === true) {
        // This is a success message
        if (document.getElementById(dict[msgFieldId]).classList.contains('alert-warning')) {
            document.getElementById(dict[msgFieldId]).classList.remove('alert-warning');
            if (document.getElementById(dict[msgFieldId]).classList.contains('alert-success')) {
                document.getElementById(dict[msgFieldId]).classList.add('alert-success');
            }
        }
    } else if (success === false) {
        // This is an error message
        if (document.getElementById(dict[msgFieldId]).classList.contains('alert-success')) {
            document.getElementById(dict[msgFieldId]).classList.remove('alert-success');
            if (document.getElementById(dict[msgFieldId]).classList.contains('alert-warning')) {
                document.getElementById(dict[msgFieldId]).classList.add('alert-warning');
            }
        }
    }
    let errorBlock = document.getElementById(msgFieldId);
    errorBlock.innerText = errorMessage;
    let errorAlert = document.getElementById(msgFieldId);
    document.getElementById(dict[msgFieldId]).style.display = 'block';
}

function updateDepartmentsDropdown(departments_list) {
    let optionsHtml = '';
    for (let i = 0; i < departments_list.length; i++) {
        optionsHtml += `<option value=${departments_list[i]}>${departments_list[i]}</option>`;
    }
    document.getElementById('selectdepartment').innerHTML = optionsHtml;
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
});
