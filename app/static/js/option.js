$('#apply_btn').on('click', function() {
    var show_already_due = 0
    if ($('#show_already_due_check').prop('checked')){
        show_already_due = 1
    }

    var settings = JSON.stringify({ "show_already_due": show_already_due });
    $.ajax({
        type: 'POST',
        url: '/settings_change',
        data: settings,
        contentType: 'application/json',
        success: function (response) {
            console.log(response);
            $('apply_msg').show('0.4')
        },
        error: function (error) {
            console.log(error);
        }
    });
})


