$('.control[data-remove-url]').on("click", function(e){
    e.preventDefault();
    var name = $(this).data('name');
    var url = $(this).data('remove-url');
    var modal = $('#delete-league-modal');
    modal.find('#league-name').html(name);
    modal.find('#delete-league-btn').attr('href', url);
    modal.modal('show');
});

$(document).ready(function(){
    $('[data-toggle="popover"]').popover({
        html: true
    });
});
