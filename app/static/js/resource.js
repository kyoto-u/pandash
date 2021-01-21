$(document).ready(function(){
    if (numofcourses > 3 ) {
        $('.ressubs').attr('style', 'height: 200px; overflow-y: scroll;')
    }

    $('a#checkedclick').on('click',function(e){
        e.preventDefault()
        var input_resources = document.querySelectorAll("input:checked");
        var r_links = new Array();
        if (0 < input_resources.length){
            for (var checked_data of input_resources){
                if(checked_data.value=="0"){
                    var selectel = 'a[name="' + checked_data.id + '"]';
                    var link = document.querySelector(selectel);
                    if(link!=null){
                        link.click();
                        r_links.push(link.getAttribute("href"));
                    }
                }
            }
            console.log(r_links)
        }
        if (r_links.length==0){
            alert("ダウンロードする資料をチェックしてください");
        }else{
            var resourcedata = JSON.stringify({"r_links":r_links});
            $.ajax({
                type: 'POST',
                url: '/r_status_change',
                data: resourcedata,
                contentType: 'application/json',
                success: function(response){
                    console.log(response);
                },
                error: function(error){
                    console.log(error);
                }
            })
        }
        return false;
    })
    $('a#allclick').on('click',function(e){
        e.preventDefault();
        var nd_resources = document.querySelectorAll("input");
        var r_links = new Array();
        if (0 < nd_resources.length){
            for (var nd_resource of nd_resources){
                var selecteall = 'a[name="' + nd_resource.id + '"]';
                var link = document.querySelector(selecteall)
                if (link!=null){
                    link.click();
                    r_links.push(link.getAttribute("href"));
                }
            }
        }
        if (r_links.length==0){
            alert("未ダウンロード資料はありません．");
        }else{
            var resourcedata = JSON.stringify({"r_links":r_links});
            $.ajax({
                type: 'POST',
                url: '/r_status_change',
                data: resourcedata,
                contentType: 'application/json',
                success: function(response){
                    console.log(response);
                },
                error: function(error){
                    console.log(error);
                }
            })
        }
        return false;
    })
})
