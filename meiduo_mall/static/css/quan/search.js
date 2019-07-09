$(document).ready(function(){
    var searchText = $("#searchText").attr("value");
    if(searchText) $("#quan-key").attr("value",searchText);
});

var stripscript = function(str) {
    var pattern = new RegExp("[`~!@#$^&*()=|{}':;',\\[\\].<>/?~！@#￥……&*（）——|{}【】‘；：”“’。，、？]");
    var rs = "";
    for (var i = 0; i < str.length; i++) {
        rs =  rs + str.substr(i, 1).replace(pattern, '');
    }
    return rs;
};

var selectSearchItem = function(_this) {
    $(".i-quan .select").removeClass('select');
    $(_this).addClass('select');
    $('.quan-tit').html($(_this).text() + '<i class="ci-right"></i>');
    var selectItem = $(".i-quan .select").attr('data-value');
    if (selectItem == 1) {
        $('#key').attr('id', 'quan-key');
    } else {
        $('#quan-key').attr('id', 'key');
    }
};

var searchCoupon = function(key) {
    var selectItem = $(".i-quan .select").attr('data-value');
    if (selectItem == 1) {
        var searchText = stripscript($('#quan-key').val());
        window.location.href = "/search.html?searchText=" + encodeURI(searchText);
    } else {
        search(key);
    }
};