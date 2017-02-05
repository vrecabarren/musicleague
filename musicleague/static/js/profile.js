var make_tile_size_consistent = function() {
    // Make all league titles center vertically w/ the tallest
    var maxTitleHeight = 0;
    $('.league-title').each(function(){
        var height = $(this).height();
        if (height > maxTitleHeight) maxTitleHeight = height;
    });
    $('.league-title').css('min-height', maxTitleHeight + 'px');

    // Make innter tile a square at minimum height
    var tileHeight = $('.league-tile-inner').first().height();
    var tileWidth = $('.league-tile-inner').first().width();
    if (tileWidth != null && tileHeight < tileWidth ) {
        $('.league-tile-inner').css('min-height', tileWidth + 'px');
    }

    // After resizing things, make sure the league items are consistent
    var maxItemHeight = 0;
    $('.league-item').each(function() {
        var height = $(this).height();
        if (height > maxItemHeight) maxItemHeight = height;
    });
    $('.league-item').css('min-height', maxItemHeight + 'px');
};

var randomize_tile_backgrounds = function() {
    // Use single league tile background shifted to random positions
    $('.league-tile').each(function(){
        var horizontalPosition = Math.floor((Math.random() * 100));
        var verticalPosition = Math.floor((Math.random() * 100));
        $(this).css('background-position', horizontalPosition + '% ' + verticalPosition + '%');
    });
};

$('.control[data-remove-url]').on("click", function(e){
    e.preventDefault();
    var name = $(this).data('name');
    var url = $(this).data('remove-url');
    var modal = $('#delete-league-modal');
    modal.find('#league-name').html(name);
    modal.find('#delete-league-btn').attr('href', url);
    modal.modal('show');
});

$(window).load(function(){
    make_tile_size_consistent();
    randomize_tile_backgrounds();
});
