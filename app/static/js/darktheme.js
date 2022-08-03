$("document").ready(function(){
    //共通部分
    logo_loc = $("#siteface").attr("src")
    logo_loc = logo_loc.replace("PandAsh_logo","PandAsh_logo_dark")
    $("#siteface").attr("src",logo_loc)
    $(".navbar-light").addClass("navbar-dark bg-dark")
    $(".navbar-light").removeClass("navbar-light bg-light")
    $(".border-dark").addClass("border-light")
    $(".navbar-brand").css("color","white")
    $(".border-dark").removeClass("border-dark")
    $(".btn-light").addClass("btn-dark")
    $(".btn-light").removeClass("btn-light")
    $(".btn-dark").addClass("btn-light")
    $(".btn-dark").removeClass("btn-dark")
    $('body').css('background-color', '#3e4347');
    $('body').css('color', 'white');
    $('#footercont').css({ "background-color": '#3e4347' });
    $(".card-header").css({ "color": "white", "background-color":"#3e4347"})
    $(".faqque").css("color","white")
    $(".card-body").css("background-color","#343a40")

    //設定
    $(".option-content").css("color", "black")
    $(".toggle-on").removeClass("btn-light")
    $(".toggle-on").addClass("btn-dark")
    $("#trial-running").css({"color":"black","background-color":"whitesmoke"})
    
    // 課題_一覧表示
    $(".fa-dumpster").css({"color":"white"})
    $(".table").css({"color":"white"})
    $(".task_link").css({ "color":"dodgerblue"})
    $(".target_select").css({ "background-color":"dimgray"})
    $(".selected_page").css({"color":"dimgray"})
    $(".another_page").css({ "color":"whitesmoke"})

    //課題_時間割表示
    $(".striped_gray").css({ "background-color":"#474d52"})
    $(".col-2>.course").css({"color":"deepskyblue"})
    $(".card.col-md-3").css({"padding-left":"0","padding-right":"0"})

    //授業資料
    $(".fa-folder>a").css({"color":"skyblue"})

    //モーダル
    $(".modal-content").css({ "background-color": "#343a40" })
    $("td>a").css({"color":"skyblue"})

    $("p>a").css({ "color": "skyblue" })
    

    //設定
    $(".option-content").css({ "color": "white", "background-color": "#2d3338" })

    //お知らせ
    $("th>a").css({"color":"white"})
    $("#message_container").css({ "background-color": "#4d5154" })
    $(".tcell_announce_overview").css({"color":"white"})
    $("tr>.col-2").css({"background-color":"inherit","color":"white"})
});