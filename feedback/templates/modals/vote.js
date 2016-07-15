$('.upvote').click(function(e) {
    e.preventDefault();
    var upvote_btn = $(this);
    var upvote_uri = upvote_btn.attr('target');
    var upvote_target = $('#' + upvote_uri);
    alert(upvote_target.attr('class'));
});

var _enableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    if (!modal.find('.has-error').length) {
        submitButton.removeClass('disabled');
        form.unbind('submit');
    }
};

var _disableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.addClass('disabled');
    form.submit(function(e) { e.preventDefault(); });
};

$('input[type=number]').on('input', function() {
    var input = $(this);
    var isNumber = input.val().match(/[0-9 -()+]+$/);
    if (isNumber) {
        input.parent('.form-group').removeClass('has-error');
        _enableVoteForm();
    }
    else {
        input.parent('.form-group').addClass('has-error');
        _disableVoteForm();
    }
});
