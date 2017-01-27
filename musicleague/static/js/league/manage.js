$('#search').bootcomplete({
    url: '{{ url_for("autocomplete") }}',
    method: 'post',
    minLength: 3
});

$('form').submit(function(){
    var members = [];
    $('#added-members .added-member').each(function() {
        members.push(String($(this).data('id')));
    });
    var inputField = $(document.getElementById('added-members-inp'));
    inputField.val(JSON.stringify(members));

    var invited = [];
    $('#added-members .invited-member').each(function() {
        invited.push(String($(this).data('email')));
    });
    var inputField = $(document.getElementById('invited-members-inp'));
    inputField.val(JSON.stringify(invited));

    var rounds = [];
    $('#added-rounds .added-round').each(function() {
        rounds.push(
            {
                'name': $(this).data('name'),
                'description': $(this).data('description'),
                'submission-due-date-utc': $(this).data('submission-due-date-utc'),
                'voting-due-date-utc': $(this).data('voting-due-date-utc')
            }
        );
    });
    var inputField = $(document.getElementById('added-rounds-inp'));
    inputField.val(JSON.stringify(rounds));

    return true;
});

$('#add-round-btn').on('click', function(){
    var roundName = $('#round-name').val();
    var roundDescription = $('#round-description').val();
    var submissionDueDate = $('#submission-due-date-utc').val();
    var votingDueDate = $('#voting-due-date-utc').val();
    $('#added-rounds').append(
        '<span class="added-round" data-name="'+roundName+'" data-description="'+roundDescription+'" data-submission-due-date-utc="'+submissionDueDate+'" data-voting-due-date-utc="'+votingDueDate+'">'+roundName+'</span>'
    );
    $('#league-rounds-save-warning').slideDown();

    $('#league-rounds input, #league-rounds textarea').val("");
    $('#round-name').focus();

    var nextSubmissionDueDate = moment.utc(submissionDueDate, "MM/DD/YY hA").add(7, 'days');
    $('#submission-due-date').val(moment(nextSubmissionDueDate.toDate()).format('MM/DD/YY hA'));
    var nextVotingDueDate = moment.utc(votingDueDate, "MM/DD/YY hA").add(7, 'days');
    $('#voting-due-date').val(moment(nextVotingDueDate.toDate()).format('MM/DD/YY hA'));
    $('#submission-due-date, #voting-due-date').trigger('dp.change');
});

$('#send-email-btn').on('click', function(){
    var email = $('#email').val();
    $('#added-members').append(
        '<span class="invited-member" data-email="'+email+'">'+email+'</span>'
    );
    $('#email').val("");
    $('#added-members').trigger('contentchanged');
});

$('#the-basics input').keydown(function() {
    if ( $(this).val() != $(this).data('og')) {
        $('#the-basics-save-warning').slideDown();
    }
});

$('#added-members').on('contentchanged', function() {
    $('#league-members-save-warning').slideDown();
});

$('#submission-due-date').datetimepicker({
    sideBySide: true,
    format: 'MM/DD/YY hA',
    useStrict: true,
    showClose: true
}).on("dp.change", function(e) {
    $('#submission-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
    $('#voting-due-date').data("DateTimePicker").minDate(e.date.add(1, 'hours').toDate());
});

$('#voting-due-date').datetimepicker({
    sideBySide: true,
    format: 'MM/DD/YY hA',
    useStrict: true,
    showClose: true
}).on("dp.change", function(e) {
    $('#voting-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
});

$('.btn-edit').on("click", function() {
    var round = $(this).parent();
    var id = round.data('id');
    var name = round.data('name');
    var description = round.data('description');
    var submissionDueDateUTC = round.data('submission-due-date-utc');
    var submissionDueDate = moment.utc(submissionDueDateUTC, "MM/DD/YY hA").toDate();
    var votingDueDateUTC = round.data('voting-due-date-utc');
    var votingDueDate = moment.utc(votingDueDateUTC, "MM/DD/YY hA").toDate();

    var modal = $('#edit-round-modal');
    modal.find('#edit-name').val(name);
    modal.find('#edit-description').val(description);
    modal.find('#edit-submission-due-date').val(moment(submissionDueDate).format('MM/DD/YY hA'));
    modal.find('#edit-voting-due-date').val(moment(votingDueDate).format('MM/DD/YY hA'));

    modal.modal('show');
});

$(document).ready(function() {
    switch (window.location.hash) {

        case '#members':
            $('.collapse').collapse('hide');
            $('#league-members').collapse('show');
            var pos = $('#league-members-header').offset();
            $('body').animate({ scrollTop: pos.top });
            break;

        case '#rounds':
            $('.collapse').collapse('hide');
            $('#league-rounds').collapse('show');
            var pos = $('#league-rounds-header').offset();
            $('body').animate({ scrollTop: pos.top });
            break;

        default:
            break;
    }
});
