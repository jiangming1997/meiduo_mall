/**
 * Created by cengxiangjie on 2016/5/8.
 */

$(document).ready(function(){
    // 查询礼包和专属券数量
    aladdinObj.queryCouponNum(function(res){
        if (res.error) {
            $(".quantarget").html("<li><a class='openLogin' href='javascript:void(0);'><span class='txt'>你好，请先登录</span></a></li>");

            $(".openLogin").bind('click',function(){
                vipCheckLogin(location.href);
            });
        } else {
            $(".quantarget li:eq(0)").find("a").find("em").text(res.specialNum);
            $(".quantarget li:eq(1)").find("a").find("em").text(res.giftNum);

            $.getJSON("//quan.jd.com/getcouponcount.action?callback=?", function (a) {
                a.CouponCount && $(".quantarget li:eq(2)").find(".uc-num").text(a.CouponCount);
            });
            if(res.giftNum>0){
                $("#treasure").html("<a href='javaScript:openGift()'><img src='//img20.360buyimg.com/uba/jfs/t6772/43/796251452/2898/655b0fb/5979ae25Nd7206ead.png' alt='我的专属优惠券!' clstag='pageclick|keycount|aladdin_201605165|23'/></a>");
            }else if(res.specialNum>0){
                $("#treasure").html("<a href='/specials.html'><img src='//img20.360buyimg.com/uba/jfs/t6772/43/796251452/2898/655b0fb/5979ae25Nd7206ead.png' alt='我的专属优惠券!' clstag='pageclick|keycount|aladdin_201605165|23'/></a>");
            }
        }
    });

    // 首页专属券链接登录拦截
    $("#nav-specials").bind('click',function(){
        vipCheckLogin("/specials.html");
    });
});

// 查询礼包列表
seajs.use([
    'jdf/1.0.0/ui/dialog/1.0.0/dialog',
    'jdf/1.0.0/ui/scrollbar/1.0.0/scrollbar',
    'jdf/1.0.0/ui/drag/1.0.0/drag',
    'jdf/1.0.0/ui/switchable/1.0.0/switchable'
],function(){
    $('.openGift').bind('click',function(){
        openGift();
    });
});

function sEvent(){
    $('.gifts-box').switchable({
        type:'slider',
        navItem:'ui-sg-item',
        navSelectedClass:'curr',
        contentClass:'ui-sg-panel-main',//主体
        mainClass:'ui-sg-panel',
        prevClass:'ui-sg-prev',
        nextClass:'ui-sg-next',
        hasPage:true,
        autoPlay:false
    });
}

function openGift(){
    seajs.use([
        'jdf/1.0.0/ui/dialog/1.0.0/dialog',
        'jdf/1.0.0/ui/scrollbar/1.0.0/scrollbar',
        'jdf/1.0.0/ui/drag/1.0.0/drag',
        'jdf/1.0.0/ui/switchable/1.0.0/switchable'
    ],function() {
        $.ajax({
            url: "/myCoupon/queryGift.html?r=" + Math.random(),
            data: "",
            type: "post",
            dataType: "json",
            async: true,
            success: function (res) {
                if (res.success) {
                    if ("true" == res.errorMsg) {
                        $('body').dialog({
                            title: '我的优惠券礼包',
                            width: 500,
                            height: 300,
                            type: 'text',
                            mainId: 'quan-dialog5',
                            source: $('#gift02').html()
                        });
                    } else {
                        var giftPackageVoList = res.giftPackageList;
                        var len = giftPackageVoList.length;
                        if (len == 1) {
                            $('body').dialog({
                                title: '我的优惠券礼包',
                                width: 500,
                                height: 300,
                                type: 'text',
                                mainId: 'quan-dialog5',
                                source: $('#gift06').html(),
                                onReady: function () {
                                    var gift = giftPackageVoList[0];
                                    $("#gift05-page-list-item").find("div:eq(1)").html(gift.name);
                                    $("#gift05-page-list-item").find("div:eq(2)").find("a").attr("href", "javascript:getPackage(" + gift.rid + ");");
                                    $("#gift05-page-list-item").attr("id", "gift05-page-list-item-" + gift.rid);
                                    sEvent();
                                }
                            });
                        } else {
                            $('body').dialog({
                                title: '我的优惠券礼包',
                                width: 500,
                                height: 300,
                                type: 'text',
                                mainId: 'quan-dialog5',
                                source: $('#gift05').html(),
                                onReady: function () {
                                    var num = Math.ceil(len / 2);
                                    var use = 0;
                                    for (var i = 0; i < num; i++) {
                                        var pref = "gift05-page0" + (i + 1) + "-list";
                                        if (i > 0) {
                                            $("#gift05-page").append($("#gift05-page01").clone(true));
                                            $("#gift05-page").find("div:eq(" + 10 * i + ")").attr("id", "gift05-page0" + (i + 1));
                                            $("#gift05-page0" + (i + 1)).find("div:eq(0)").attr("id", pref);
                                            $("#gift05-ctrl").append($("#gift05-ctrl-01").clone(true));
                                            $("#gift05-ctrl").find("a:eq(1)").attr("class", "ui-sg-item");
                                            $("#gift05-ctrl").find("a:eq(1)").html((i + 1));
                                        }
                                        for (var m = 0; m < 2; m++) {
                                            var gift = giftPackageVoList[use];
                                            if (use == 0 || (i > 0 && use < len)) {
                                                $("#" + pref).find("div:eq(" + 4 * m + ")").find("div:eq(1)").html(gift.name);
                                                $("#" + pref).find("div:eq(" + 4 * m + ")").find("div:eq(2)").find("a").attr("href", "javascript:getPackage(" + gift.rid + ");");
                                                $("#" + pref).find("div:eq(" + 4 * m + ")").attr("id", "gift05-page-list-item-" + gift.rid);
                                                use++;
                                            } else if (i == 0 && use < len) {
                                                $("#gift05-page01-list").append($("#gift05-page01-list").find("div:eq(0)").clone(true));
                                                $("#gift05-page01-list").find("div:eq(4)").attr("id", "gift05-page-list-item-" + gift.rid);
                                                var name = "gift05-page-list-item-" + gift.rid;
                                                $("#" + name).find("div:eq(1)").html(gift.name);
                                                $("#" + name).find("div:eq(2)").find("a").attr("href", "javascript:getPackage(" + gift.rid + ");");
                                                use++;
                                            } else {
                                                $("#" + pref).find("div:eq(" + 4 * m + ")").remove();
                                                use++;
                                            }
                                        }
                                    }
                                    sEvent();
                                }
                            });
                        }

                    }
                } else {
                    $('body').dialog({
                        title: '我的优惠券礼包',
                        width: 500,
                        height: 300,
                        type: 'text',
                        mainId: 'quan-dialog5',
                        source: $('#gift02').html(),
                        onReady: function () {
                            $('#gift02-error').html(res.errorMsg);
                        }
                    });

                }
            },
            error: function (data, status, e) {
                $('body').dialog({
                    title: '我的优惠券礼包',
                    width: 500,
                    height: 300,
                    type: 'text',
                    mainId: 'quan-dialog5',
                    source: $('#gift02').html(),
                    onReady: function () {
                        $('#gift02-error').html("系统出了点小故障！");
                    }
                });
            }
        });
    })
}

// 获取礼包
var getPackageResult = {}; //KEY是礼包ID，Value是领取结果，查看礼包的时候用
function getPackage(id){
    seajs.use([
        'jdf/1.0.0/ui/dialog/1.0.0/dialog',
        'jdf/1.0.0/ui/scrollbar/1.0.0/scrollbar',
        'jdf/1.0.0/ui/drag/1.0.0/drag',
        'jdf/1.0.0/ui/switchable/1.0.0/switchable'
    ],function(){

        function sEvent(){
            $('.gifts-box').switchable({
                type:'slider',
                navItem:'ui-sg-item',
                navSelectedClass:'curr',
                contentClass:'ui-sg-panel-main',//主体
                mainClass:'ui-sg-panel',
                prevClass:'ui-sg-prev',
                nextClass:'ui-sg-next',
                hasPage:true,
                autoPlay:false
            });
        }
        $.ajax({
            url: "/myCoupon/getGift.html?r="+Math.random(),
            data: {"rid":id},
            type: "post",
            dataType: "json",
            async: true,
            success: function (res) {
                if(res.success){
                    getPackageResult[id] = res;//查看礼包的时候用checkPackage()
                    $("#gift05-page-list-item-"+id).find("div:eq(0)").find("img").attr("src","img/img3.png");

                    if (res.giftPackageList && res.giftPackageList.length>0) {
                        $("#gift05-page-list-item-"+id).find("div:eq(2)").find("a").attr("href","javascript:checkPackage("+id+");");
                        $("#gift05-page-list-item-"+id).find("div:eq(2)").find("a").html("查看详情");

                    }else {
                        $("#gift05-page-list-item-"+id).find("div:eq(2)").find("a").attr("href","javascript:void(0);");
                        $("#gift05-page-list-item-"+id).find("div:eq(2)").find("a").html("礼包是空的");
                    }

                    $(".quantarget li:eq(1)").find("a").find("em").html(res.giftNum);
                }else{
                    $('body').dialog({
                        title:'我的优惠券礼包',
                        width:500,
                        height:300,
                        type:'text',
                        mainId:'quan-dialog5',
                        source:$('#gift02').html(),
                        onReady:function(){
                            $('#gift02-error').html(res.errorMsg);
                        }
                    });
                }
            },
            error: function (data, status, e) {
                $('body').dialog({
                    title:'我的优惠券礼包',
                    width:500,
                    height:300,
                    type:'text',
                    mainId:'quan-dialog5',
                    source:$('#gift02').html(),
                    onReady:function(){
                        $('#gift02-error').html("系统出了点小故障！");
                    }
                });
            }
        });
    });
}

// 查询礼包明细
function checkPackage(id){
    seajs.use([
        'jdf/1.0.0/ui/dialog/1.0.0/dialog',
        'jdf/1.0.0/ui/scrollbar/1.0.0/scrollbar',
        'jdf/1.0.0/ui/drag/1.0.0/drag',
        'jdf/1.0.0/ui/switchable/1.0.0/switchable'
    ],function(){

        function sEvent(){
            $('.gifts-box').switchable({
                type:'slider',
                navItem:'ui-sg-item',
                navSelectedClass:'curr',
                contentClass:'ui-sg-panel-main',//主体
                mainClass:'ui-sg-panel',
                prevClass:'ui-sg-prev',
                nextClass:'ui-sg-next',
                hasPage:true,
                autoPlay:false
            });
        }

        $('body').dialog({
            title:'我的优惠券礼包',
            width:500,
            height:300,
            type:'text',
            mainId:'quan-dialog4',
            source:$('#gift04').html(),
            onReady:function(){

                var giftPackage = getPackageResult[id].giftPackageList;
                // 礼包 data
                var giftPackageList = giftPackage[0];
                // 礼包内的礼品集合 data
                var giftPackageVoList = giftPackageList.giftInfoList;
                var len = giftPackageVoList.length;

                // gift04 礼包 dom
                var gift04 = $(".ui-dialog [name='gift04']");

                // 礼包名称
                var gift04_Name = $(".ac.fz14.mb10", gift04);
                gift04_Name.html(giftPackageList.name);


                // gift04-panel-main 礼品容器
                var gift04_PaneMain = $(".ui-sg-panel-main", gift04);


                // ui-sg-panel 一页礼品的容器，每页3个
                var gift04_PaneTemplate = $(".ui-sg-panel", gift04).clone(true);


                // gift-item 单个礼品
                var gift04_ItemTemplate = $(".gift-item", gift04).clone(true);

                // 删掉模板数据
                gift04_PaneMain.html("");
                $(".gift-list", gift04_PaneTemplate).html("");


                // 循环礼品数据
                var gift04_Pane;

                for(var i=0; i<len; i++){
                    var giftPresentDTO  = giftPackageVoList[i];

                    // 每三次一个新pane
                    if (i % 3 === 0) {
                        gift04_Pane = gift04_PaneTemplate.clone(true);
                        gift04_PaneMain.append(gift04_Pane);

                        if (i>0) {
                            $("#gift04-ctrl").append($("#gift04-ctrl-01").clone(true));
                            $("#gift04-ctrl").find("a:eq(1)").html((i+1));
                        }
                    }


                    // item加到pane里
                    var gift04_Item = gift04_ItemTemplate.clone(true);
                    var name = "";
                    if (giftPresentDTO.presentType == 1) {
                        name = "优惠券：" + giftPresentDTO.presentName;
                    }else if (giftPresentDTO.presentType == 2) {
                        name = "京豆" + giftPresentDTO.beanCount + "个";
                    }else if (giftPresentDTO.presentType == 4 || giftPresentDTO.presentType == 8) {
                        name = "金融券：" + giftPresentDTO.presentName;
                    }else{
                        name = giftPresentDTO.presentName;
                    }

                    $(".g-type", gift04_Item).html(name);
                    $(".gift-list", gift04_Pane).append(gift04_Item);
                }

                sEvent();
            }
        });

    });
}

function close(ob){
    if(4==ob){
        $(".ui-dialog-close:eq(1)").trigger("click");
    }else{
        $(".ui-dialog-close").trigger("click");
    }
}

var vipCheckLogin = function(url){
    seajs.use([
        'jdf/1.0.0/unit/login/1.0.0/login.js'
    ],function(login){
        login({
            modal:true,
            complete:function(){
                window.location.href = url;
            }
        });
    });
};