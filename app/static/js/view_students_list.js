$('.student-delete-btn').on('click', function () {
    let student_id = $(this).parent().siblings()[0].innerText;

    let url = `update_students/${student_id}`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'mode': 'delete',
            'student_id': student_id,
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

});
