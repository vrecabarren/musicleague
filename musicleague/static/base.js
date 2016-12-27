$('.linked').on("click", function() {
    var url = $(this).attr('data-href');
    window.location.href = url;
});

$(document).ready(function() {
    setTimeout(function() {
        $(".alert-auto-dismiss").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 4000);
});
