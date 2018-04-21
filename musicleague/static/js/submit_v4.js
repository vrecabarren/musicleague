
function setSongStateFound(song, track) {
    var id = track.id;
    var uri = track.uri;
    var url = track.external_urls.spotify;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;

    song.data('id', id);
    song.data('uri', uri);
    song.find('.you-selected').html('You Selected:');
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html('<a href="' + url + '" target="_blank">' + name + '</a>');
    song.find('.song-info .artist').html("By " + artist);
    song.find('.song-info .album').html(album);
    song.find('.find-song-inp').val("");
    song.removeClass('warning').removeClass('error').addClass('found');
}

function setSongStateNotFound(song) {
    song.data('id', "");
    song.data('uri', "");
    song.find('.you-selected').html('No Result:');
    song.find('.song-info img').attr('src', 'https://s3.amazonaws.com/musicleague-static-assets/icons/attentionicon.svg');
    song.find('.song-info .name').html("No luck.<br>We couldn't<br>find that.");
    song.find('.song-info .artist').html("");
    song.find('.song-info .album').html("");
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('warning').addClass('error').addClass('not-found');
}

function setSongStateDuplicateArtist(song, track) {
    var id = track.id;
    var uri = track.uri;
    var url = track.external_urls.spotify;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;

    song.data('id', id);
    song.data('uri', uri);
    song.find('.you-selected').html('Great Minds Think Alike:');
    song.find('.message').html('Someone else has already submitted a song from this artist. Proceed at your own risk!');
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html('<a href="' + url + '" target="_blank">' + name + '</a>');
    song.find('.song-info .artist').html("By " + artist);
    song.find('.song-info .album').html(album);
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('error').addClass('warning').addClass('duplicate-artist');
}

function setSongStateDuplicateAlbum(song, track) {
    var id = track.id;
    var uri = track.uri;
    var url = track.external_urls.spotify;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;

    song.data('id', id);
    song.data('uri', uri);
    song.find('.you-selected').html('Great Minds Think Alike:');
    song.find('.message').html('Someone else has already submitted a song from this album. Proceed at your own risk!');
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html('<a href="' + url + '" target="_blank">' + name + '</a>');
    song.find('.song-info .artist').html("By " + artist);
    song.find('.song-info .album').html(album);
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('error').addClass('warning').addClass('duplicate-album');
}

function setSongStateDuplicateSong(song, track) {
    var id = track.id;
    var uri = track.uri;
    var url = track.external_urls.spotify;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;

    song.data('id', id);
    song.data('uri', uri);
    song.find('.you-selected').html('Great Minds Think Alike:');
    song.find('.message').html('Someone else has already submitted this song. Try again!');
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html('<a href="' + url + '" target="_blank">' + name + '</a>');
    song.find('.song-info .artist').html("By " + artist);
    song.find('.song-info .album').html(album);
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('warning').addClass('error').addClass('duplicate-song');
}

function setSongStateRepeatSubmission(song, track) {
    var id = track.id;
    var uri = track.uri;
    var url = track.external_urls.spotify;
    var img_src = track.album.images[1].url;
    var name = track.name;
    var artist = track.artists[0].name;
    var album = track.album.name;
    var lastSubmittedDate = repeatSubmissions[uri][0];
    var lastSubmittedLeague = repeatSubmissions[uri][1];

    song.data('id', id);
    song.data('uri', uri);
    song.find('.you-selected').html('Great Minds Think Alike:');
    song.find('.message').html('Did you know you’ve submitted this song before? You last submitted it on <strong>'+lastSubmittedDate+'</strong> in the <strong>'+lastSubmittedLeague+'</strong> league.');
    song.find('.song-info img').attr('src', img_src);
    song.find('.song-info .name').html('<a href="' + url + '" target="_blank">' + name + '</a>');
    song.find('.song-info .artist').html("By " + artist);
    song.find('.song-info .album').html(album);
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('error').addClass('warning').addClass('repeat-submission');
}

function setSongStateDuplicateSubmission(song) {
    song.data('id', "");
    song.data('uri', "");
    song.find('.you-selected').html('There Must Be An Echo In Here:');
    song.find('.song-info img').attr('src', 'https://s3.amazonaws.com/musicleague-static-assets/icons/attentionicon.svg');
    song.find('.song-info .name').html("Duplicate<br>Submissions<br>Not Allowed.");
    song.find('.song-info .artist').html("");
    song.find('.song-info .album').html("");
    song.find('.find-song-inp').val("");
    song.removeClass('found').removeClass('warning').addClass('error').addClass('duplicate-submission');
}

$.fn.filterByData = function(prop, val) {
    return this.filter(
        function() { return $(this).data(prop)==val; }
    );
}

$('.find-song-inp').on("input propertychange", function(){
    var song = $(this).parent().parent();
    var url_or_uri = $(this).val();
    console.log(url_or_uri);

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
    else
        return;

    // Clear this song's URI/ID so it doesn't appear as a duplicate
    song.data('id', "");
    song.data('uri', "");

    if (trackId && $('.song').filterByData('id', trackId).length > 0) {
        setSongStateDuplicateSubmission(song);
        setSelectedSongCount();
        setSubmitButtonState();
        return;
    }

    if (trackId) {
        // Get info from Spotify API
        $.ajax({
            url: 'https://api.spotify.com/v1/tracks/' + trackId,
            headers: {
                'Authorization': 'Bearer ' + accessToken
            }
        }).done(function(response){
            setSongStateFound(song, response);
        }).fail(function(){
            setSongStateNotFound(song);
        }).always(function(){
            setSelectedSongCount();
            setSubmitButtonState();
        });
    } else {
        setSongStateNotFound(song);
        setSelectedSongCount();
        setSubmitButtonState();
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
    $('.song.found, .song.warning.duplicate-artist, .song.warning.duplicate-album, .song.error.duplicate-song, .song.warning.repeat-submission').each(function(){
        var song = $(this);
        var uri = song.data('uri');
        var uri_regex = /spotify\:track\:([a-zA-Z0-9]{22})/;
        var trackId = uri.match(uri_regex)[1];
        $.ajax({
            url: 'https://api.spotify.com/v1/tracks/' + trackId,
            headers: {
                'Authorization': 'Bearer ' + accessToken
            }
        }).success(
            function(response){
                if (song.is('.song.found')) {
                    setSongStateFound(song, response);
                } else if (song.is('.song.warning.duplicate-artist')) {
                    setSongStateDuplicateArtist(song, response);
                } else if (song.is('.song.warning.duplicate-album')) {
                    setSongStateDuplicateAlbum(song, response);
                } else if (song.is('.song.error.duplicate-song')) {
                    setSongStateDuplicateSong(song, response);
                } else if (song.is('.song.warning.repeat-submission')) {
                    setSongStateRepeatSubmission(song, response);
                }
            }
        );
    });
}

function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

function setSelectedSongCount() {
    var numSelected = $('.song.found').length;
    $('#progress #num-selected').html(pad(numSelected));
    return numSelected;
}

function setSubmitButtonState() {
    var numSelected = $('.song.found').length + $('.song.warning').length;
    var numTotal = $('.song').length;

    // If not all songs selected, disable submit button. Otherwise, enable.
    if (numSelected != numTotal) {
        $('#submit-songs-btn-wrapper').addClass('disabled');
        $('#submit-songs-btn').addClass('disabled');
        $('#submit-songs-btn').attr('disabled', 'disabled');
    } else {
        $('#submit-songs-btn').removeAttr('disabled');
        $('#submit-songs-btn').removeClass('disabled');
        $('#submit-songs-btn-wrapper').removeClass('disabled');
    }
}

$(document).ready(function() {
    $("#status-bar").stick_in_parent();
    $('form').trigger("reset").submit(processFormSubmission);
    setPreviousSubmissionState();
    setSelectedSongCount();
    setSubmitButtonState();
});
