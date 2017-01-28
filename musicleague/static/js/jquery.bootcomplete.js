/*
* @name jQuery.bootcomplete
* @projectDescription Lightweight AJAX autocomplete for Bootstrap 3
* @author Rick Somers | http://getwebhelp.com/bootcomplete
* @version 1.0
* @license MIT License
*
*/
(function ( $ ) {

    $.fn.bootcomplete = function(options) {

        var defaults = {
            url : "/search.php",
            method : 'get',
            wrapperClass : "bc-wrapper",
            menuClass : "bc-menu",
            idField : true,
            idFieldName : $(this).attr('name')+"_id",
            minLength : 3,
            dataParams : {},
            formParams : {}
        }

        var settings = $.extend( {}, defaults, options );

        $(this).attr('autocomplete','off')
        $(this).wrap('<div class="'+settings.wrapperClass+'"></div>')
        if (settings.idField) {
            if ($(this).parent().parent().find('input[name="' + settings.idFieldName + '"]').length !== 0) {
                //use existing id field
            } else {
                //there is no existing id field so create one
                $('<input type="hidden" name="' + settings.idFieldName + '" value="">').insertBefore($(this))
            }
        }
        $('<div class="'+settings.menuClass+' list-group"></div>').insertAfter($(this))

        $(this).on("keyup", searchQuery);
        $(this).on("keydown", traverseQuery);
        $(this).on("focusout", hideThat)

        var xhr;
        var that = $(this)

        function hideThat() {
            if ($('.list-group-item' + ':hover').length) {
                return;
            }
            $(that).next('.' + settings.menuClass).hide();
        }

        function searchQuery(){

            var arr = [];
            $.each(settings.formParams,function(k,v){
                arr[k]=$(v).val()
            })
            var dyFormParams = $.extend({}, arr );
            var Data = $.extend({query: $(this).val()}, settings.dataParams, dyFormParams);

            if(!Data.query){
                $(this).next('.'+settings.menuClass).html('')
                $(this).next('.'+settings.menuClass).hide()
            }

            if(Data.query.length >= settings.minLength){

                if(xhr && xhr.readyState != 4){
                    xhr.abort();
                }

                xhr = $.ajax({
                    type: settings.method,
                    url: settings.url,
                    data: Data,
                    dataType: "json",
                    success: function( json ) {
                        var results = ''
                        $.each( json, function(i, j) {
                            results += '<a href="" class="list-group-item" data-id="'+j.id+'" data-label="'+j.label+'">'+j.label+'</a>'
                        });

                        $(that).next('.'+settings.menuClass).html(results);
                        $(that).next('.'+settings.menuClass).children().on("click", selectResult);
                        $(that).next('.'+settings.menuClass).show();

                    }
                })
            }
        }

        function traverseQuery(e){
            switch(e.which) {

                case 13: //enter
                    break;

                case 38: // up
                    break;

                case 40: // down
                    break;

                default: return; // exit this handler for other keys
            }
            e.preventDefault();
        }

        function selectResult(){
            $(that).val('');
            $(that).focus();
            if (settings.idField) {
                var inputs = $(that).parent().parent().find('input[name="' + settings.idFieldName + '"]');
                if (inputs.length !== 0) {
                    var addedMember = '<span class="member added-member" data-id="'+$(this).data('id')+'" data-name="'+$(this).data('label') +'">'+$(this).data('label')+'&nbsp;</span>';
                    $('#added-members').append(addedMember);
                    addedMember = $('#added-members').children().last();
                    var deleteButton = $('<a class="btn delete-member-btn">Delete</a>');
                    deleteButton.on("click", deleteMember);
                    addedMember.append(deleteButton);
                    $('#added-members').trigger('contentchanged');
                }
            }
            $(that).next('.' + settings.menuClass).hide();
            return false;
        }

        return this;
    };

}( jQuery ));
