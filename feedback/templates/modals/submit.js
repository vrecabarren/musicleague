$('.track-input').change(function() {
    var input = $(this);
    var player = $($(this).siblings('iframe')[0]);
    var playerSrc = 'https://embed.spotify.com/?uri=' + input.val() + '&theme=white'
    player.attr('src', 'https://embed.spotify.com/?uri=' + input.val());
    input.attr('type', 'hidden');
    player.css('display', 'block');
});

$('#cancel').click(function() {
    $('iframe').css('display', 'none');
    $('.track-input').attr('type', 'text');
    $('.track-input').val('');
    $('iframe').attr('src', '');
});
