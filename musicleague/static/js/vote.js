$('.up-btn').on("click", function() {
    var wrapper = $(this).parent();
    var voteCount = wrapper.find('.vote-count');

    wrapper.addClass("voted");
    var votes = Number(voteCount.html()) + 1;
    voteCount.html(votes);

    if (votes > 0)
        wrapper.addClass("voted");
    else
        wrapper.removeClass("voted");
});

$('.down-btn').on("click", function() {
    var wrapper = $(this).parent();
    var voteCount = wrapper.find('.vote-count');
    var votes = Number(voteCount.html()) - 1;
    voteCount.html(votes);

    if (votes > 0)
        wrapper.addClass("voted");
    else
        wrapper.removeClass("voted");
});
