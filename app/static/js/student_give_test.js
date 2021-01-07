// Display the alert message
$('.alert').alert()

// function for determining if test is ready for submission
function isTestReadyForSubmission() {
    // check if all questions are answered
    let questions = $('.question');

    for (let i = 0; i < questions.length; i++) {
        let name = questions[i].value;
        let radiobutton = $(`input:radio[name*=${name}]`);
        if (!radiobutton.is(':checked')) {
            return false;
        }
    }
    return true;
}

// Submit test
$('#submit-test-btn').on('click', function () {
    // isTestReadyForSubmission();
    if (isTestReadyForSubmission()) {
        // submit the test
        let classtestpost_id = $('#post-id').val();
        let questions = $('.question');

        let qans = {};

        for (let i = 0; i < questions.length; i++) {
            let name = questions[i].value;
            let radiobutton = $(`input:radio[name*=${name}]:checked`);
            qans[parseInt(name)] = parseInt(radiobutton.val());
        }

        // Submit the data to the backend
        let url = window.location.href;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'classtestpost_id': classtestpost_id,
                'qans': qans,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['process'] === 'success') {
                window.history.back();
            } else {
                // The request failed. Display the appropriate error message sent back in response.
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });
    } else {
        // display error message
        displayFormErrorMessage(false, 'Please answer all the questions', 'alertmessage');
    }
});