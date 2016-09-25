var _enableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.removeClass('disabled');
    form.unbind('submit');
};

var _disableVoteForm = function() {
    var modal = $('#vote-modal');
    var form = modal.find('form');
    var submitButton = modal.find('button[type="submit"]');
    submitButton.addClass('disabled');
    form.submit(function(e) { e.preventDefault(); });
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
    sum = sumPoints();
    if (sum != {{ league.preferences.point_bank_size }})
        _disableVoteForm();
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
    sumPoints();
    setFormState();
};
