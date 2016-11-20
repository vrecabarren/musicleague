    $(function() {
        $( "#add_user" ).autocomplete({
            source: function( request, response ) {
                $.ajax({
                    url: "/autocomplete/",
                    dataType: "json",
                    data: {term: request.term},
                    success: function( data ) {
                        console.log(data);
                        response(
                            $.map(data, function( item ) {
                                return {
                                    label: item.name,
                                    value: item.email
                                }
                            })
                        );
                    }
                });
            },
            select: function( event, ui ) {
                $.post("{{ url_for('add_user_for_league', league_id=league.id) }}",
                    {email: ui.item.value},
                    function(data, textStatus, xhr){
                        location.reload();
                    }
                );
                return false;
            },
            minLength: 2
        });
        $( "#add_user" ).autocomplete( "option", "appendTo", "#add_user_div");
    });
