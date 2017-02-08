function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

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
    song.find('.find-song-inp').val("");
    song.find('.find-song-btn').html('Change It!');
    song.addClass('found');

    var numSelected = parseInt($('#progress #num-selected').html());
    $('#progress #num-selected').html(pad(++numSelected));
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
                setSongStateFound(song, response);
            });
        }
});

function collectSongs() {
    var songs = [];
    $('.song').each(function() {
        songs.push(String($(this).data('uri')));
    });
    var jsonField = $(document.getElementById('songs-inp'));
    jsonField.val(JSON.stringify(songs));
}

function processFormSubmission() {
    collectSongs();
    return true;
}

function setPreviousSubmissionState() {
    $('.song.found').each(function(){
        var song = $(this);
        var uri = song.data('uri');
        var uri_regex = /spotify\:track\:([a-zA-Z0-9]{22})/;
        var trackId = uri.match(uri_regex)[1];
        $.ajax({url: 'https://api.spotify.com/v1/tracks/' + trackId}).success(
            function(response){
                setSongStateFound(song, response);
            }
        );
    });
}

$(document).ready(function() {
    $('form').submit(processFormSubmission);
    setPreviousSubmissionState();
});
