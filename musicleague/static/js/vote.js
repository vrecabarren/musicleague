function pad(n) {
    return (n < 10) ? ("0" + n) : n;
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
        currentTotalSpent += 1;
        totalSpentContainer.html(pad(currentTotalSpent));
        wrapper.addClass("voted");
    }

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
        currentTotalSpent -= 1;
        totalSpentContainer.html(pad(currentTotalSpent));
    }

    if (currentSongSpent == 0) {
        wrapper.removeClass("voted");
    }

    setSubmitButtonState();
}

$('.up-btn').on("click", function() {
    var song = $(this).parent().parent();
    setSongStateUpvote(song);
});

$('.down-btn').on("click", function() {
    var song = $(this).parent().parent();
    setSongStateDownvote(song);
});
