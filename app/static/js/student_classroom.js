// Posts filter
$('#subjectfilter').on('change', function () {
    let class_name = $(this).val();
    let posts = $('.posts');

    for (let i = 0; i < posts.length; i++) {
        if (posts[i].classList.contains('hidepost')) {
            posts[i].classList.remove('hidepost');
        }
    }

    if (class_name !== 'all') {
        for (let i = 0; i < posts.length; i++) {
            if (!posts[i].classList.contains('hidepost') && !posts[i].classList.contains(class_name)) {
                posts[i].classList.add('hidepost');
            }
        }
    }
});

// reload this page every 300 seconds (5 mins)
setInterval(function() {
    window.location.reload();
}, 5*60000);
