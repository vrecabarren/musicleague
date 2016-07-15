var _disableEditLeagueForm = function () {
    var modal = $('#edit-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.addClass('disabled');
    form.submit(function(e) { e.preventDefault(); });
};

var _enableEditLeagueForm = function () {
    var modal = $('#edit-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    if (!modal.find('.has-error').length) {
        submitButton.removeClass('disabled');
        form.unbind('submit');
    }
};

$('#name').on('input', function () {
    var input = $(this);
    var isName = input.val();
    if (isName) {
        input.parent('.form-group').removeClass('has-error');
        _enableEditLeagueForm();
    }
    else {
        input.parent('.form-group').addClass('has-error');
        _disableEditLeagueForm();
    }
});

$('#track_count,#submission_reminder_time').on('input', function () {
    var input = $(this);
    var isNumber = input.val().match(/[0-9 -()+]+$/);
    if (isNumber) {
        input.parent('.form-group').removeClass('has-error');
        _enableEditLeagueForm();
    }
    else {
        input.parent('.form-group').addClass('has-error');
        _disableEditLeagueForm();
    }
});
