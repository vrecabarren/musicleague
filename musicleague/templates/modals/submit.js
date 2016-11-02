var _enableSubmitForm = function() {
    var modal = $('#submit-modal');
    var form = modal.find('form');

    var addTrackBtn = modal.find('#btnAddTrack');
    addTrackBtn.addClass('disabled');

    var submitButton = modal.find('button[type="submit"]');
    submitButton.removeClass('disabled');
    form.unbind('submit');
    form.submit(function(e) {

    });
};

var _disableSubmitForm = function() {
    var modal = $('#submit-modal');
    var form = modal.find('form');

    var addTrackBtn = modal.find('#btnAddTrack');
    addTrackBtn.removeClass('disabled');

    var submitButton = modal.find('button[type="submit"]');
    submitButton.addClass('disabled');
    form.submit(function(e) { e.preventDefault(); });
};

var allTracksFilled = function() {
    return $('.track-placeholder').length <= 0;
};

var setSubmitFormState = function() {
    if (allTracksFilled())
        _enableSubmitForm();
    else
        _disableSubmitForm();
};

$('.track-input').change(function() {
    var input = $(this);
    var player = $($(this).siblings('iframe')[0]);
    player.attr('src', 'https://embed.spotify.com/?uri=' + input.val());
});

$('#btnAddTrack').on('click', function() {
    var spotifyUri = $('#inpAddTrack').val();
    var playerSrc = 'https://embed.spotify.com/?uri=' + spotifyUri;
    $('#inpAddTrack').val("");
    var trackPlaceholder = $('div .track-placeholder').first();
    trackPlaceholder.html('<iframe width="100%" height="80" frameborder="0" allowtransparency="true" src="' + playerSrc + '"></iframe>');
    trackPlaceholder.attr('id', spotifyUri);
    trackPlaceholder.removeClass('track-placeholder');
    trackPlaceholder.css('padding', '10px');
    setSubmitFormState();
});
