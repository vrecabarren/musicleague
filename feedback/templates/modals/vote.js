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
    var isPositive = Number(input.val()) >= 0;
    if (isNumber && isPositive) {
        var sum = 0;
        $('#vote-modal input[type=number]').each(function() {
            sum += Number($(this).val());
        });

        if (sum == {{ league.preferences.point_bank_size }})
        {
            $('#vote-modal .form-group').removeClass('has-error');
            _enableVoteForm();
            return;
        }
    }

    input.parent('.form-group').addClass('has-error');
    _disableVoteForm();
});
