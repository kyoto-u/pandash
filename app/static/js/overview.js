$(function() {
    $("#finish_form").droppable({
      accept: ".taskcard",
      scroll: false,
      tolerance: "touch",
      activeClass: "active-d", //Draggable要素がドラッグしている際に適用
      hoverClsaa: "hover-d",   //Draggable要素が上に乗った時に適用
      drop: function(event, ui){
        dr_text = ui.draggable.find("a").text();
        dr_id = ui.draggable.find("a").attr("href");
        var add_f_task = $("<li></li>");
        add_f_task.html(dr_text);
        $(this).append(add_f_task);
        ui.draggable.remove();
        var dr_ids = new Array();
        dr_ids.push(dr_id);
        var task_id = JSON.stringify({"task_id":dr_ids});
        $.ajax({
          type: "POST",
          url: "/task_finish",
          data: task_id,
          contentType: "application/json",
          success: function(response){
            console.log(response);
          },
          error: function(error){
            console.log(error);
          }
        })
      }
    });
    $(".taskcard").draggable({
      helper: "clone",
      revert: "invalid",
      start: function(event, ui){
        $("#overview_table").removeClass("table-responsive");
      },
      stop: function(event, ui){
        $("#overview_table").addClass("table-responsive");
      }
    });
})
