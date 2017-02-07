function setSongStateFound(song, track) {
    var id = track.id;
    var uri = track.uri;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;

    song.data('id', id);
    song.data('uri', uri);
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html(name);
    song.find('.song-info .artist').html(artist);
    song.find('.song-info .album').html(album);
    song.addClass('found');
}

$('.find-song-btn').on("click", function(){
    var song = $(this).parent().parent().parent();
    var url_or_uri = song.find('.find-song-inp').val();

    var url_play_regex = /play\.spotify\.com\/track\/([a-zA-Z0-9]{22})/;
    var url_open_regex = /open\.spotify\.com\/track\/([a-zA-Z0-9]{22})/;
    var uri_regex = /spotify\:track\:([a-zA-Z0-9]{22})/;

    var trackId  = null;
    if (url_or_uri.match(url_open_regex))
        trackId = url_or_uri.match(url_open_regex)[1];
    else if (url_or_uri.match(url_play_regex))
        trackId = url_or_uri.match(url_play_regex)[1];
    else if (url_or_uri.match(uri_regex))
        trackId = url_or_uri.match(uri_regex)[1];

    if (trackId != null) {
        // Get info from Spotify API
        $.ajax({url: 'https://api.spotify.com/v1/tracks/' + trackId}).success(
            function(response){
                var name = response.name;
                var artist = response.artists[0].name;
                setSongStateFound(song, response);
            });
        }
});
