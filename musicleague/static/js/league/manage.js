
// Initialize league member search autocomplete
$('#search').bootcomplete({
    url: '/autocomplete/',
    method: 'post',
    minLength: 3
});

// Initialize league round add datetime pickers
function initializeDatePicker(elementId) {
    return $(elementId).datetimepicker({
        sideBySide: true,
        format: 'MM/DD/YY hA',
        useStrict: true,
        showClose: true
    });
};
initializeDatePicker('#submission-due-date').on("dp.change", function(e) {
    $('#submission-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
    $('#voting-due-date').data("DateTimePicker").minDate(e.date.add(1, 'hours').toDate());
});
initializeDatePicker('#voting-due-date').on("dp.change", function(e) {
    $('#voting-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
});
initializeDatePicker('#edit-submission-due-date').on("dp.change", function(e) {
    $('#edit-submission-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
    $('#edit-voting-due-date').data("DateTimePicker").minDate(e.date.add(1, 'hours').toDate());
});
initializeDatePicker('#edit-voting-due-date').on("dp.change", function(e) {
    $('#edit-voting-due-date-utc').val(moment(e.date.utc()).format('MM/DD/YY hA'));
});

// Process submission for manage league form
function collectAddedMembers() {
    var members = [];
    $('#added-members .added-member').each(function() {
        members.push(String($(this).data('id')));
    });
    var jsonField = $(document.getElementById('added-members-inp'));
    jsonField.val(JSON.stringify(members));
};

function collectInvitedMembers() {
    var invited = [];
    $('#added-members .invited-member').each(function() {
        invited.push(String($(this).data('email')));
    });
    var jsonField = $(document.getElementById('invited-members-inp'));
    jsonField.val(JSON.stringify(invited));
};

function collectDeletedMembers() {
    var members = [];
    $('#added-members .deleted-member').each(function() {
        members.push(String($(this).data('id')));
    });
    var jsonField = $(document.getElementById('deleted-members-inp'));
    jsonField.val(JSON.stringify(members));
};

function collectAddedRounds() {
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
    var jsonField = $(document.getElementById('added-rounds-inp'));
    jsonField.val(JSON.stringify(rounds));
};

function collectEditedRounds() {
    var rounds = [];
    $('#added-rounds .edited-round').each(function() {
        rounds.push(
            {
                'id': String($(this).data('id')),
                'name': $(this).data('name'),
                'description': $(this).data('description'),
                'submission-due-date-utc': $(this).data('submission-due-date-utc'),
                'voting-due-date-utc': $(this).data('voting-due-date-utc')
            }
        );
    });
    var jsonField = $(document.getElementById('edited-rounds-inp'));
    jsonField.val(JSON.stringify(rounds));
};

function collectDeletedRounds() {
    var rounds = [];
    $('#added-rounds .deleted-round').each(function() {
        rounds.push(String($(this).data('id')));
    });
    var jsonField = $(document.getElementById('deleted-rounds-inp'));
    jsonField.val(JSON.stringify(rounds));
};

function processFormSubmission() {
    collectAddedMembers();
    collectInvitedMembers();
    collectDeletedMembers();
    collectAddedRounds();
    collectEditedRounds();
    collectDeletedRounds();
    return true;
};

// Remove member
function deleteMember() {
    var member = $(this).parent().parent();
    var deletedId = member.data('id');
    var deletedName = member.data('name');
    member.find('.member-name').html('<s>'+deletedName+'</s>');
    member.find('.delete-member-btn').remove();
    var undoButton = $('<a class="btn undelete-member-btn">Undo</a>');
    undoButton.on("click", undeleteMember);
    member.find('.button-wrapper').append(undoButton);

    if (member.hasClass('current-member')) {
        member.data('prev-class', 'current-member');
        member.removeClass('current-member');
    } else if (member.hasClass('added-member')) {
        member.data('prev-class', 'added-member');
        member.removeClass('added-member');
    } else if (member.hasClass('invited-member')) {
        member.data('prev-class', 'invited-member');
        member.removeClass('invited-member');
    }
    member.addClass('deleted-member');

    $('#league-members').trigger('contentchanged');
};

function undeleteMember() {
    var member = $(this).parent().parent();
    var undeletedId = member.data('id');
    var undeletedName = member.data('name');
    member.find('.member-name').html(undeletedName);
    member.find('.undelete-member-btn').remove();
    var deleteButton = $('<a class="btn delete-member-btn">Delete</a>');
    deleteButton.on("click", deleteMember);
    member.find('.button-wrapper').append(deleteButton);
    var prevClass = member.data('prev-class');
    member.removeClass('deleted-member').addClass(prevClass);

    $('#league-members').trigger('contentchanged');
};

// Add invited member
function inviteMember() {
    var email = $('#email').val();
    var addedMember = '<span class="row member invited-member" data-name="'+email+'" data-email="'+email+'"><div class="col-xs-9 member-name-wrapper"><span class="member-name">'+email+'</span></div><div class="col-xs-3 button-wrapper"></div></span>';
    $('#added-members').append(addedMember);
    addedMember = $('#added-members').children().last();
    var deleteButton = $('<a class="btn delete-member-btn">Delete</a>');
    deleteButton.on("click", deleteMember);
    addedMember.find('.button-wrapper').append(deleteButton);
    $('#email').val("");
    $('#league-members').trigger('contentchanged');
};

// Add round to league on button click
function guid() { return Math.floor((1 + Math.random()) * 0x10000).toString(16); }
function addRound() {
    // Generate a random id for correlation when editing added round
    var roundId = guid();
    var roundName = $('#round-name').val();
    var roundDescription = $('#round-description').val();
    var submissionDueDate = $('#submission-due-date-utc').val();
    var votingDueDate = $('#voting-due-date-utc').val();

    var newRound = $('<span class="row round added-round" data-id="'+roundId+'" data-name="'+roundName+'" data-description="'+roundDescription+'" data-submission-due-date-utc="'+submissionDueDate+'" data-voting-due-date-utc="'+votingDueDate+'"></span>');
    $('#added-rounds').append(newRound);
    newRound = $('#added-rounds').children().last();
    newRound.append('<div class="col-xs-6 col-sm-8 col-md-7 round-name-wrapper"><span class="round-name">'+roundName+'</span></div><div class="col-xs-3 col-sm-2 button-wrapper"></div><div class="col-xs-3 col-sm-2 col-md-3 button-wrapper"></div>');

    var editRoundButton = $('<a class="btn edit-round-btn">Edit</a>');
    editRoundButton.on("click", editRound);
    newRound.find('.button-wrapper').eq(0).append(editRoundButton);

    var deleteRoundButton = $('<a class="btn delete-round-btn">Delete</a>');
    deleteRoundButton.on("click", deleteRound);
    newRound.find('.button-wrapper').eq(1).append(deleteRoundButton);

    $('#league-rounds input, #league-rounds textarea').val("");
    $('#round-name').focus();

    var nextSubmissionDueDate = moment.utc(submissionDueDate, "MM/DD/YY hA").add(7, 'days');
    $('#submission-due-date').val(moment(nextSubmissionDueDate.toDate()).format('MM/DD/YY hA'));
    $('#submission-due-date-utc').val(nextSubmissionDueDate.format('MM/DD/YY hA'));

    var nextVotingDueDate = moment.utc(votingDueDate, "MM/DD/YY hA").add(7, 'days');
    $('#voting-due-date').val(moment(nextVotingDueDate.toDate()).format('MM/DD/YY hA'));
    $('#voting-due-date-utc').val(nextVotingDueDate.format('MM/DD/YY hA'));

    $('#league-rounds').trigger('contentchanged');
};

// Handle edit round modal on button click
$('#edit-round-modal').on('shown.bs.modal', function(){
    $('#edit-name').focus();
});
function editRound() {
    var round = $(this).parent().parent();
    var id = round.data('id');
    var name = round.data('name');
    var description = round.data('description');
    var submissionDueDateUTC = round.data('submission-due-date-utc');
    var submissionDueDate = moment.utc(submissionDueDateUTC, "MM/DD/YY hA").toDate();
    var votingDueDateUTC = round.data('voting-due-date-utc');
    var votingDueDate = moment.utc(votingDueDateUTC, "MM/DD/YY hA").toDate();

    var modal = $('#edit-round-modal');
    modal.find('#edit-id').val(id);
    modal.find('#edit-name').val(name);
    modal.find('#edit-description').val(description);
    modal.find('#edit-submission-due-date').val(moment(submissionDueDate).format('MM/DD/YY hA'));
    modal.find('#edit-submission-due-date-utc').val(moment(submissionDueDateUTC, 'MM/DD/YY hA').format('MM/DD/YY hA'));
    modal.find('#edit-voting-due-date').val(moment(votingDueDate).format('MM/DD/YY hA'));
    modal.find('#edit-voting-due-date-utc').val(moment(votingDueDateUTC, 'MM/DD/YY hA').format('MM/DD/YY hA'));

    modal.modal('show');
};

// Update data properties on round from modal
function commitEditRound() {
    var modal = $('#edit-round-modal');
    var editedId = modal.find('#edit-id').val();
    var editedName = modal.find('#edit-name').val();
    var editedDescription = modal.find('#edit-description').val();
    var editedSubmissionDueDateUTC = modal.find('#edit-submission-due-date-utc').val();
    var editedVotingDueDateUTC = modal.find('#edit-voting-due-date-utc').val();

    var round = $('.round[data-id="'+editedId+'"]');
    round.data('name', editedName);
    round.data('description', editedDescription);
    round.data('submission-due-date-utc', editedSubmissionDueDateUTC);
    round.data('voting-due-date-utc', editedVotingDueDateUTC);
    round.find('.round-name').html(editedName);
    if (round.hasClass('current-round'))
        round.removeClass('current-round').addClass('edited-round');
    modal.modal('hide');

    $('#league-rounds').trigger('contentchanged');
};

// Update data properties on round being deleted
function deleteRound() {
    var round = $(this).parent().parent();
    var deletedId = round.data('id');
    var deletedName = round.data('name');
    round.find('.round-name').html('<s>'+deletedName+'</s>');
    round.find('.edit-round-btn').remove();
    round.find('.delete-round-btn').remove();
    var undoButton = $('<a class="btn undelete-round-btn">Undo</a>');
    undoButton.on("click", undeleteRound);
    round.find('.button-wrapper').eq(1).append(undoButton);

    if (round.hasClass('current-round')) {
        round.data('prev-class', 'current-round');
        round.removeClass('current-round');
    } else if (round.hasClass('added-round')) {
        round.data('prev-class', 'added-round');
        round.removeClass('added-round');
    } else if (round.hasClass('edited-round')) {
        round.data('prev-class', 'edited-round');
        round.removeClass('edited-round');
    }

    round.addClass('deleted-round');

    $('#league-rounds').trigger('contentchanged');
};

function undeleteRound() {
    var round = $(this).parent().parent();
    var undeletedName = round.data('name');
    round.find('.round-name').html(undeletedName);
    round.find('.undelete-round-btn').remove();
    var editButton = $('<a class="btn edit-round-btn">Edit</a>');
    editButton.on("click", editRound);
    round.find('.button-wrapper').eq(0).append(editButton);
    var deleteButton = $('<a class="btn delete-round-btn">Delete</a>');
    deleteButton.on("click", deleteRound);
    round.find('.button-wrapper').eq(1).append(deleteButton);
    var prevClass = round.data('prev-class');
    round.removeClass('deleted-round').addClass(prevClass);

    $('#league-rounds').trigger('contentchanged');
};

// Bind all event handlers
$(document).ready(function() {
    $('form').submit(processFormSubmission);
    $('#send-email-btn').on('click', inviteMember);
    $('.delete-member-btn').on('click', deleteMember);
    $('#add-round-btn').on('click', addRound);
    $('.edit-round-btn').on("click", editRound);
    $('#edit-round-btn').on("click", commitEditRound);
    $('.delete-round-btn').on("click", deleteRound);
    $('.undelete-round-btn').on("click", undeleteRound);

    $('#the-basics').on('contentchanged', function() { $('#the-basics-save-warning').slideDown(); });
    $('#the-basics').on('contentunchanged', function() { $('#the-basics-save-warning').slideUp(); });
    $('#league-members').on('contentchanged', function() { $('#league-members-save-warning').slideDown(); });
    $('#league-rounds').on('contentchanged', function() { $('#league-rounds-save-warning').slideDown(); });
    $('#the-basics input').keydown(function() {
        if ( $(this).val() != $(this).data('ov'))
            $('#the-basics').trigger('contentchanged');
    });
});
