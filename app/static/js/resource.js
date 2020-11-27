function somewindowopen() {

    var input_resources = document.querySelectorAll("input:checked");
    if (0<input_resources.length){
        for (var checked_data of input_resources){
            console.log(checked_data.id)
            alert(checked_data.id)
        }
    }

    // window.open("http://www.yahoo.co.jp/", "_blank");
    // window.open("https://www.google.co.jp/", "_blank");
    // window.open("https://teratail.com/", "_blank");
    return false;
}

function checkedlist_click(){
    var input_resources = document.querySelectorAll("input:checked");
    var is_checked = Boolean(false);
    if (0 < input_resources.length){
        for (var checked_data of input_resources){
            if(checked_data.value=="0"){
                var selectel = 'a[name="' + checked_data.id + '"]';
                var link = document.querySelector(selectel);
                if(link!=null){
                    link.click();
                    is_checked = true;
                }
            }
        }
    }
    if (!is_checked){
        alert("ダウンロードする資料をチェックしてください");
    }
    return false;
}

function all_click(){
    var resources = document.querySelectorAll("input");
    if (0 < resources.length){
        for (var resource of resources){
            if (resource.value=="0"){
                var selectel = 'a[name="' + resource.id + '"]';
                var link = document.querySelector(selectel);
                if(link!=null){
                    link.click();
                }
            }
        }
    }
    return false;
}
