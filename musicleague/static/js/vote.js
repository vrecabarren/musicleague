function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

function setSongStateUpvote(song) {
    var wrapper = song.find('.up-down-btn-wrapper');
    var voteCount = wrapper.find('.vote-count');
    var votes = Number(voteCount.html()) + 1;
    var currentVotes = $('#num-spent');
    var numMaxVotes = Number($('#max-votes').html());

    if (votes <= numMaxVotes) {
        wrapper.addClass("voted");
        voteCount.html(votes);
        var newCurrentVotes = Number(currentVotes.html()) + 1;
        currentVotes.html(pad(newCurrentVotes));
    } else if (votes > numMaxVotes) {
        wrapper.addClass("voted");
    } else {
        wrapper.removeClass("voted");
    }
}

function setSongStateDownvote(song) {
    var wrapper = song.find('.up-down-btn-wrapper');
    var voteCount = wrapper.find('.vote-count');
    var votes = Number(voteCount.html()) - 1;
    var currentVotes = $('#num-spent');

    if (votes > 0) {
        wrapper.addClass("voted");
        voteCount.html(votes);
        var newCurrentVotes = Number(currentVotes.html()) + 1;
        currentVotes.html(pad(newCurrentVotes));
    } else if (votes == 0) {
        wrapper.removeClass("voted");
        voteCount.html(votes);
        var newCurrentVotes = Number(currentVotes.html()) + 1;
        currentVotes.html(pad(newCurrentVotes));
    } else {
        wrapper.removeClass("voted");
    }
}

$('.up-btn').on("click", function() {
    var song = $(this).parent().parent();
    setSongStateUpvote(song);
});

$('.down-btn').on("click", function() {
    var song = $(this).parent().parent();
    setSongStateDownvote(song);
});
