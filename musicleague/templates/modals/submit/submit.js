$('.track-input').change(function() {
    var input = $(this);
    var player = $($(this).siblings('iframe')[0]);
    var playerSrc = 'https://embed.spotify.com/?uri=' + input.val() + '&theme=white'
    player.attr('src', 'https://embed.spotify.com/?uri=' + input.val());
});
