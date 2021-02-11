$(document).ready(function () {
    let updateBtn = $('#details-update-btn');
    updateBtn.hide();
    let ogEmail = $('#email').val();
    let ogFirstName = $('#first_name').val();
    let ogLastName = $('#last_name').val();

    $(document).on('keyup', '#email', function () {
        if($(this).val() !== ogEmail) {
            updateBtn.show();
        } else {
            updateBtn.hide();
        }
    });

    $(document).on('keyup', '#first_name', function () {
        if($(this).val() !== ogFirstName) {
            updateBtn.show();
        } else {
            updateBtn.hide();
        }
    });

    $(document).on('keyup', '#last_name', function () {
        if($(this).val() !== ogLastName) {
            updateBtn.show();
        } else {
            updateBtn.hide();
        }
    });


    // Cancel plan
    $(document).on('click', '#cancel-plan-btn', function () {
        let cancelUrl = '/college/cancel_plan';
        let college_id = $('#college').val();

        fetch(cancelUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'college_id': college_id,
            }),
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if(data['process'] === 'success') {
                location.replace('/college/plan_cancelled');
            } else {
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });

    });

});