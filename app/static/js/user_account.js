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

});