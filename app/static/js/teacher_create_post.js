
// Utility functions for hiding and showing UI elements based on user selection
function showClassTestPostBody() {
    let classtestpostbody = $('.classtestpostbody')[0];
    if (classtestpostbody.classList.contains('hidepost')) {
        classtestpostbody.classList.remove('hidepost');
    }
}

function hideClassTestPostBody() {
    let classtestpostbody = $('.classtestpostbody')[0];
    if (!classtestpostbody.classList.contains('hidepost')) {
        classtestpostbody.classList.add('hidepost');
    }
}

function showPostCategory() {
    let postcategory = $('.postcategory')[0];
    if (postcategory.classList.contains('hidepost')) {
        postcategory.classList.remove('hidepost');
    }
}

function hidePostCategory() {
    let postcategory = $('.postcategory')[0];
    if (!postcategory.classList.contains('hidepost')) {
        postcategory.classList.add('hidepost');
    }
}

function showTextPostBody() {
    let textpostbody = $('.textpostbody')[0];
    if (textpostbody.classList.contains('hidepost')) {
        textpostbody.classList.remove('hidepost');
    }
}

function hideTextPostBody() {
    let textpostbody = $('.textpostbody')[0];
    if (!textpostbody.classList.contains('hidepost')) {
        textpostbody.classList.add('hidepost');
    }
}

function showVideoPostBody() {
    let videopostbody = $('.videopostbody')[0];
    if (videopostbody.classList.contains('hidepost')) {
        videopostbody.classList.remove('hidepost');
    }
}

function hideVideoPostBody() {
    let videopostbody = $('.videopostbody')[0];
    if (!videopostbody.classList.contains('hidepost')) {
        videopostbody.classList.add('hidepost');
    }
}

function showDocumentPostBody() {
    let documentpostbody = $('.documentpostbody')[0];
    if (documentpostbody.classList.contains('hidepost')) {
        documentpostbody.classList.remove('hidepost');
    }
}

function hideDocumentPostBody() {
    let documentpostbody = $('.documentpostbody')[0];
    if (!documentpostbody.classList.contains('hidepost')) {
        documentpostbody.classList.add('hidepost');
    }
}

function showImagePostBody() {
    let imagepostbody = $('.imagepostbody')[0];
    if (imagepostbody.classList.contains('hidepost')) {
        imagepostbody.classList.remove('hidepost');
    }
}

function hideImagePostBody() {
    let imagepostbody = $('.imagepostbody')[0];
    if (!imagepostbody.classList.contains('hidepost')) {
        imagepostbody.classList.add('hidepost');
    }
}

function showYoutubePostBody() {
    let youtubepostbody = $('.youtubepostbody')[0];
    if (youtubepostbody.classList.contains('hidepost')) {
        youtubepostbody.classList.remove('hidepost');
    }
}

function hideYoutubePostBody() {
    let youtubepostbody = $('.youtubepostbody')[0];
    if (!youtubepostbody.classList.contains('hidepost')) {
        youtubepostbody.classList.add('hidepost');
    }
}

function showArticlePostBody() {
    let linkpostbody = $('.articlepostbody')[0];
    if (linkpostbody.classList.contains('hidepost')) {
        linkpostbody.classList.remove('hidepost');
    }
}

function hideArticlePostBody() {
    let linkpostbody = $('.articlepostbody')[0];
    if (!linkpostbody.classList.contains('hidepost')) {
        linkpostbody.classList.add('hidepost');
    }
}

// Post type selection
$('#postcategory').on('change', function () {
    switch ($(this).val()) {
        case "textpost":
            showTextPostBody();
            hideArticlePostBody();
            hideYoutubePostBody();
            hideImagePostBody();
            hideDocumentPostBody();
            hideVideoPostBody();
            break;
        case "videopost":
            showVideoPostBody();
            hideTextPostBody();
            hideArticlePostBody();
            hideYoutubePostBody();
            hideImagePostBody();
            hideDocumentPostBody();
            break
        case "documentpost":
            showDocumentPostBody();
            hideVideoPostBody();
            hideTextPostBody();
            hideArticlePostBody();
            hideYoutubePostBody();
            hideImagePostBody();
            break
        case "imagepost":
            showImagePostBody();
            hideDocumentPostBody();
            hideVideoPostBody();
            hideTextPostBody();
            hideArticlePostBody();
            hideYoutubePostBody();
            break
        case "youtubepost":
            showYoutubePostBody();
            hideImagePostBody();
            hideDocumentPostBody();
            hideVideoPostBody();
            hideTextPostBody();
            hideArticlePostBody();
            break
        case "articlepost":
            showArticlePostBody();
            hideImagePostBody();
            hideDocumentPostBody();
            hideVideoPostBody();
            hideTextPostBody();
            hideYoutubePostBody();
            break
    }
});

// If ClasstestPost radio button is selected show classtestpost UI elements and hide others
$('.posttype').on('click', function () {
    if ($('#postype1').prop('checked')) {
        hideClassTestPostBody();
        showPostCategory();
        showTextPostBody();
    } else if ($('#postype2').prop('checked')) {
        hideClassTestPostBody();
        showPostCategory();
        showTextPostBody();
    } else if ($('#postype3').prop('checked')) {
        hideArticlePostBody();
        hideYoutubePostBody();
        hideImagePostBody();
        hideDocumentPostBody();
        hideVideoPostBody();
        hideTextPostBody();
        hidePostCategory();
        showClassTestPostBody();
    }
});

// ClasstestPost adding more questions and ans
let questionNo = 2;
let optionNo = 3;

// add another option on button click
$('body').on('click', '#addoptionbtn', function () {
    if (optionNo < 5) {
        let optionHtml = '<div class="form-group row opt">' +
            `<label for="q${(questionNo - 1)}o${optionNo}" class="col-1 opt-label">${optionNo}.</label>` +
            '<input type="text" class="form-control form-control-sm col-11 opt-input"' +
            `name="q${(questionNo - 1)}o${optionNo}" id="q${(questionNo - 1)}o${optionNo}" placeholder="Option ${optionNo}">` +
            '</div>';

        $(optionHtml).insertBefore($(this));

        let correctOptionHtml = `<option value="q${(questionNo - 1)}o${optionNo}">${optionNo}</option>`;
        $(`#ans${(questionNo - 1)}`).append(correctOptionHtml);

        optionNo++;

        if (optionNo > 4) {
            $(this).remove();
        }

    }
});

// add another question on button click
$('#addquestionbtn').on('click', function () {
    optionNo = 3;
    let questionHtml = '<br><br><div class="classtestqna">' +
        '<div class="form-group">' +
        `<label for="q${questionNo}">Question ${questionNo}:</label>` +
        `<input type="text" class="form-control form-control-sm" name="q${questionNo}"` +
        `id="q${questionNo}" placeholder="What is the capital of India?">` +
        '</div>' +
        '<div class="form-group row opt">' +
        `<label for="q${questionNo}o1" class="col-1 opt-label">1.</label>` +
        '<input type="text" class="form-control form-control-sm col-11 opt-input"' +
        `name="q${questionNo}o1" id="q${questionNo}o1" placeholder="Option 1">` +
        '</div>' +
        '<div class="form-group row opt">' +
        `<label for="q${questionNo}o2" class="col-1 opt-label">2.</label>` +
        '<input type="text" class="form-control form-control-sm col-11 opt-input"' +
        `name="q${questionNo}o2" id="q${questionNo}o2" placeholder="Option 2">` +
        '</div>' +
        '<button type="button" class="btn btn-secondary" id="addoptionbtn">' +
        '+ option' +
        '</button>' +
        '<div class="input-group-prepend float-right">' +
        `<label for="ans${questionNo}">Answer:&nbsp;</label>` +
        `<select class="form-control btn-secondary" id="ans${questionNo}">` +
        `<option value="q${questionNo}o1">1</option>` +
        `<option value="q${questionNo}o2">2</option>` +
        '</select>' +
        '</div>' +
        '</div><br>';

    $(questionHtml).insertBefore($(this));
    $('#totalnoofquestions').val(questionNo);
    questionNo++;
});
