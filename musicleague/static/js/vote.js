function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

function setSongStateUpvote(song) {
    var wrapper = song.find('.up-down-btn-wrapper');
    var totalSpentContainer = $('#num-spent');
    var songSpentContainer = wrapper.find('.vote-count');

    var maxTotalSpent = Number($('#max-votes').html());
    var currentTotalSpent = Number(totalSpentContainer.html());
    var currentSongSpent = Number(songSpentContainer.html());
    var remaining = maxTotalSpent - currentTotalSpent;


    if (remaining >= 1) {
        remaining -= 1;
        currentSongSpent += 1;
        songSpentContainer.html(currentSongSpent);
        song.data("votes", currentSongSpent);
        wrapper.addClass("voted");
    }

    setSpentVotesCount();
    setSubmitButtonState();
}

function setSongStateDownvote(song) {
    var wrapper = song.find('.up-down-btn-wrapper');
    var totalSpentContainer = $('#num-spent');
    var songSpentContainer = wrapper.find('.vote-count');

    var maxTotalSpent = Number($('#max-votes').html());
    var currentTotalSpent = Number(totalSpentContainer.html());
    var currentSongSpent = Number(songSpentContainer.html());
    var remaining = maxTotalSpent - currentTotalSpent;


    if (currentSongSpent > 0 && currentTotalSpent > 0) {
        currentSongSpent -= 1;
        songSpentContainer.html(currentSongSpent);
        song.data("votes", currentSongSpent);
    }

    if (currentSongSpent == 0) {
        wrapper.removeClass("voted");
    }

    setSpentVotesCount();
    setSubmitButtonState();
}

$('.up-btn').on("click", function() {
    var song = $(this).parent().parent().parent();
    setSongStateUpvote(song);
});

$('.down-btn').on("click", function() {
    var song = $(this).parent().parent().parent();
    setSongStateDownvote(song);
});

function setPreviousVoteState() {
    $('.song').each(function() {
        var numVotes = Number($(this).data("votes"));
        if (numVotes) {
            $(this).find('.up-down-btn-wrapper').addClass("voted");
            $(this).find('.vote-count').html(numVotes);
        }
    });
}

function setSpentVotesCount() {
    var total = 0;
    $('.song').each(function() {
        var numVotes = Number($(this).data("votes"));
        if (numVotes > 0) {
            total += numVotes;
        }
    });
    $('#num-spent').html(pad(total));
}

function setSubmitButtonState() {
    var maxTotalSpent = Number($('#max-votes').html());
    var currentTotalSpent = Number($('#num-spent').html());

    var submitVotesBtnWrapper = $('#submit-votes-btn-wrapper');
    var submitVotesBtn = submitVotesBtnWrapper.find('#submit-votes-btn');

    if (currentTotalSpent == maxTotalSpent) {
        submitVotesBtnWrapper.removeClass("disabled");
        submitVotesBtn.removeClass("disabled");
        submitVotesBtn.removeAttr("disabled");
    } else {
        submitVotesBtnWrapper.addClass("disabled");
        submitVotesBtn.addClass("disabled");
        submitVotesBtn.attr("disabled", "true");
    }
}

function collectVotes() {
    var votes = {};
    $('.song').each(function() {
        var uri = $(this).data("uri");
        var numVotes = Number($(this).data("votes"));
        votes[uri] = numVotes;
    });

    var jsonField = $(document.getElementById('votes-inp'));
    jsonField.val(JSON.stringify(votes));
}

function processFormSubmission() {
    collectVotes();
    return true;
}

$(document).ready(function() {
    $("#status-bar").stick_in_parent();
    $('form').trigger("reset").submit(processFormSubmission);
    setPreviousVoteState();
    setSpentVotesCount();
    setSubmitButtonState();
});
