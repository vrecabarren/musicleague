$(function () {
    $('#submission_due_date').val(moment('{{ submission_period.submission_due_date }}').toDate());
    $('#submission_due_date').datetimepicker({
        sideBySide: false,
        format: 'dddd MM/DD/YY hA',
        useStrict: true,
        showClose: true
    }).on("dp.change", function(e) {
        $('#submission_due_date_utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
    });

    $('#voting_due_date').val(moment('{{ submission_period.vote_due_date }}').toDate());
    $('#voting_due_date').datetimepicker({
        sideBySide: false,
        format: 'dddd MM/DD/YY hA',
        useStrict: true,
        showClose: true
    }).on("dp.change", function(e) {
        $('#voting_due_date_utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
    });
});

$(document).ready(function(){
    var localSubmissionDueDate = moment.utc('{{ submission_period.submission_due_date }}').toDate();
    $('#submission_due_date').val(moment(localSubmissionDueDate).format('dddd MM/DD/YY hA'));
    $('#submission_due_date_utc').val(moment(moment.utc('{{ submission_period.submission_due_date }}')).format('MM/DD/YY hA'));

    var localVotingDueDate = moment.utc('{{ submission_period.vote_due_date }}').toDate();
    $('#voting_due_date').val(moment(localVotingDueDate).format('dddd MM/DD/YY hA'));
    $('#voting_due_date_utc').val(moment(moment.utc('{{ submission_period.vote_due_date }}')).format('MM/DD/YY hA'));

    $('[data-toggle="popover"]').popover();
});
