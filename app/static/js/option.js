$('#show_already_due_check').change(function(){
    var show_already_due = 0;
    if($(this).prop('checked')){
        show_already_due = 1;
    }
    var data = JSON.stringify({"show_already_due":show_already_due});
    $.ajax({
        type: 'POST',
        url: '/show_already_due',
        data: data,
        contentType: 'application/json',
        success: function (response) {
            console.log(response);
            $('#cancel_msg').fadeOut();
            $('#apply_msg').fadeOut();
            $('#apply_msg').show('0.4');
        },
        error: function (error) {
            console.log(error);
            $('#apply_msg').fadeOut();
            $('#cancel_msg').fadeOut();
            $('#cancel_msg').show('0.4');
        }
    });
})

$(".course_checkbox").change(function(){
    var prop = $(this).prop('checked');
    var course_list = new Array();
    var hide = 1;
    if(prop){
        hide = 0;
    }
    course_list.push($(this).val());
    data = JSON.stringify({"course_list":course_list, "hide":hide})
    $.ajax({
        type: 'POST',
        url: '/course_hide',
        data: data,
        contentType: 'application/json',
        success: function (response) {
            console.log(response);
            $('#cancel_msg').fadeOut();
            $('#apply_msg').fadeOut();
            $('#apply_msg').show('0.4');
        },
        error: function (error) {
            console.log(error);
            $('#apply_msg').fadeOut();
            $('#cancel_msg').fadeOut();
            $('#cancel_msg').show('0.4');
        }
    });

})
