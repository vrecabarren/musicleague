var _enableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.removeClass('disabled');
    form.unbind('submit');
    form.submit(function(e) {
        var votes = {};
        $('#staging .vote-count').each(function() {
            var voteCount = parseInt($(this).text());
            var uri = $(this).parents('.track').first().attr('id');
            var inputField = $(document.getElementById(uri));
            inputField.val(voteCount);
        });

        var modal = $('#vote-modal');
        var form = modal.find('form').first();
        return true;
    });
};

var _disableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.addClass('disabled');
    form.submit(function(e) { e.preventDefault(); });
};

var setLoadState = function() {
    $('#selection .track').each(function() {
        var voteCount = parseInt($(this).find($('.vote-count')).first().text());
        if (voteCount > 0)
        {
            $('#staging').append($(this));
            $(this).find('.voting-controls').css('display', 'flex');
            $(this).off("click");
        }
    });
};

var setFormState = function() {
    if (allPointsAssigned())
        _enableVoteForm();
    else
        _disableVoteForm();
};

var sumPoints = function() {
    var sum = 0;
    $('#staging .vote-count').each(function() {
        sum += Number($(this).text());
    });
    $('#remaining').html({{ league.preferences.point_bank_size }} - sum);
    return sum;
};

var allPointsAssigned = function() {
    var pointsRemaining = parseInt($('#remaining').text());
    return pointsRemaining == 0;
};

$(document).ready(function() {
    setLoadState();
    sumPoints();
    setFormState();

    $('#staging .voting-controls').css('display', 'flex');
});

$('.vote-up').on("click", function() {
    var voteCountSpan = $(this).parent().parent().find($('.vote-count')).first();
    var voteCount = parseInt(voteCountSpan.text());
    voteCount += 1;
    voteCountSpan.text(voteCount);
    sumPoints();
    setFormState();
});

$('.vote-down').on("click", function() {
    var voteCountSpan = $(this).parent().parent().find($('.vote-count')).first();
    var voteCount = parseInt(voteCountSpan.text());
    if (voteCount > 0)
        voteCount -= 1;
    voteCountSpan.text(voteCount);
    sumPoints();
    setFormState();
});

var drag = function(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

var allowDrop = function(ev) {
    ev.preventDefault();
};

var dropSelection = function(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var track = $(document.getElementById(data));
    $('#selection').append(track);
    track.find('.voting-controls').css('display', 'none');
    sumPoints();
    setFormState();
};

var dropStaging = function(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var track = $(document.getElementById(data));
    $('#staging').append(track);
    track.find('.voting-controls').css('display', 'flex');
    track.off("click");
    sumPoints();
    setFormState();
};

$('#selection .track').on("click", function() {
    $('#staging').append($(this));
    $(this).find('.voting-controls').css('display', 'flex');
    $(this).off("click");
    sumPoints();
    setFormState();
});
