$('.linked').on("click", function() {
    var url = $(this).attr('data-href');
    window.location.href = url;
});
