// For comments feature
$(document).ready(function () {
    $('.comments-section').hide();

    let commentUrl = '/college/classroom/comment';
    let replyUrl = '/college/classroom/reply';


    let appendTo = null;
    let afterTo = null;
    let replyTo = null;

    let commentId = null;

    $(document).on('click', '.comment-btn', function () {
        commentId = null;
        $(this).siblings().toggle();
        $(this).siblings(':last').children(':last').children(':nth-child(2)').text('Add a new comment:')
    });

    $(document).on('click', '.add-comment-btn', function () {
        let postId = $(this).prop('id');
        let comment = $(this).siblings(':nth-child(3)').val();

        if (commentId === null) {
            // Post the comment
            fetch(commentUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    'post_id': postId,
                    'comment': comment,
                })
            }).then((response) => {
                return response.json();
            }).then((data) => {
                if (data['process'] === 'success') {
                    let comment_id = data['comment_id'];
                    let author = data['author'];
                    let comment = data['comment'];
                    let is_teacher = data['is_teacher'];
                    let date = data['date'];

                    let teacherMark = '<span class="teacher-tick">&#x2713;</span>';

                    if(is_teacher === 'False') {
                        teacherMark = '';
                    }

                    let newReply = '<div class="reply">' +
                        '<span class="comment-header">' +
                        `<b>${author} ${teacherMark}</b> on <span class="comment-time-stamp">${date}</span>` +
                        '</span>' +
                        `<div class="comment-body">${comment}</div>` +
                        `<button class="btn reply-reply-btn" id="${comment_id}">` +
                        '<img src="/static/icons/comment_black.svg" alt="comment icon"> <small>REPLY</small>' +
                        '</button>' +
                        '</div>';
                    $(this).parent().siblings().append(newReply);
                    location.reload();
                } else {
                    // The request failed. Display the appropriate error message sent back in response.
                    displayFormErrorMessage(false, data['msg'], 'alertmessage');
                }
            });

        } else {
            // Post the reply
            let replied_to = `<b>@${replyTo.trim()}</b>`;

            fetch(replyUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    'comment_id': commentId,
                    'replied_to': replied_to,
                    'comment': comment,
                })
            }).then((response) => {
                return response.json();
            }).then((data) => {
                if (data['process'] === 'success') {
                    commentId = null;

                    let comment_id = data['comment_id'];
                    let author = data['author'];
                    let comment = data['comment'];
                    let is_teacher = data['is_teacher'];
                    let date = data['date'];

                    let teacherMark = '<span class="teacher-tick">&#x2713;</span>';

                    if(is_teacher === 'False') {
                        teacherMark = '';
                    }

                    let newReply = '<div class="reply">' +
                        '<span class="comment-header">' +
                        `<b>${author} ${teacherMark}</b> on <span class="comment-time-stamp">${date}</span>` +
                        '</span>' +
                        `<div class="comment-body">${comment}</div>` +
                        `<button class="btn reply-reply-btn" id="${comment_id}">` +
                        '<img src="/static/icons/comment_black.svg" alt="comment icon"> <small>REPLY</small>' +
                        '</button>' +
                        '</div>';

                    if (appendTo !== null) {
                        appendTo.append(newReply);
                    } else if (afterTo !== null) {
                        afterTo.after(newReply);
                    }

                    location.reload();
                } else {
                    // The request failed. Display the appropriate error message sent back in response.
                    displayFormErrorMessage(false, data['msg'], 'alertmessage');
                }
            });
        }


    });

    $(document).on('click', '.comment-reply-btn', function () {
        commentId = $(this).prop('id');
        replyTo = $(this).siblings(':first').children(':first').text().trim();
        let label = $(this).parent().parent().siblings(':last').children(':nth-child(2)');
        appendTo = $(this).siblings(':nth-child(4)');
        label.text(`Reply to ${replyTo}:`);
    });

    $(document).on('click', '.reply-reply-btn', function () {
        commentId = $(this).prop('id');
        replyTo = $(this).siblings(':first').children(':first').text().trim();
        let label = $(this).parent().parent().parent().parent().siblings(':last').children(':nth-child(2)');
        afterTo = $(this).parent().siblings(':last');
        label.text(`Reply to ${replyTo}:`);
    });


    // Delete comments
    let baseDeleteUrl = '/college/classroom/delete_comment_or_reply/';
    $(document).on('click', '.delete-comment-btn', function () {
        let commentId = parseInt($(this).attr('id'));

        fetch(baseDeleteUrl + commentId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'comment_id': commentId,
                'reply_id': null,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if(data['process'] === 'success') {
                location.reload();
            } else {
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });

    });

    // Delete replies
    $(document).on('click', '.delete-reply-btn', function () {
        let replyId = parseInt($(this).attr('id'));

        fetch(baseDeleteUrl + replyId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'comment_id': null,
                'reply_id': replyId,
            })
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if(data['process'] === 'success') {
                location.reload();
            } else {
                displayFormErrorMessage(false, data['msg'], 'alertmessage');
            }
        });
    });

});