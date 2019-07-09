import json
import re
import time

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from weibo import APIClient

# 认证应用

from django_redis import get_redis_connection

from carts.utils import merge_cart_cookie_to_redis
from users.models import User
from .models import OAuthQQUser, OAuthSINAUser
from meiduo_mall.utils.response_code import RETCODE
from .utils import generate_openid_signature, check_openid_signature, \
    OAuthWB  # 这里导包要带本路径的标示 . or OAuth. 因为外层也有一个utils会冲突
import requests
import logging

# 日志输出器
logger = logging.getLogger()


class QQOAuth(View):
    """QQ登陆url"""

    def get(self, request):
        # 获取查询参数
        next = request.GET.get('next', '/')

        # 实例化对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        # 调用它里面的get_qq_url方法得到拼接好的QQ登录url

        login_url = oauth.get_qq_url()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQOAuthView(View):
    """处理QQ登陆状态"""

    def get(self, request):
        """OAuth 认证过程"""
        # 获取参数的code
        code = request.GET.get('code')
        # 校验code
        if code is None:
            return HttpResponse('错误')

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI
                        )
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except:
            logger.info('认证失败')
            return HttpResponse('认证失败')
        logger.info(openid)

        # """拿到openid的后续绑定或登录处理"""

        # QQ登陆用户表中的话就直接登陆没有就绑定一个用户
        try:  # 得不到报错try 一下
            qq_model = OAuthQQUser.objects.get(openid=openid)  # 匹配一个QQ用户对象

        except:
            # 如果查询不到openid,说明此QQ号是第一次来登录美多商城,应用和一个美多用户进行绑定操作
            # 把openid进行加密,加密后渲染给模板,让前端界面帮我们暂存一会openid,以备后续绑定用户时使用
            openid = generate_openid_signature(openid)
            return render(request, 'oauth_callback.html', {"openid": openid})
        else:
            # 如果查询到openid,说明此QQ已绑定过美多用户,那么直接就登录成功 返回用户名保持登录状态
            user = qq_model.user

            # 调用django自带的状态保持方法
            login(request, user)

            # 重定向到来时页面
            response = redirect(request.GET.get('state', '/'))
            # next = request.GET.get('state')
            # response = redirect(next, '/')
            # 给响应体中设置带 username 的cookie 让状态保持功能闭环
            # 设置cookie方法 set_cookie(建明，值，时间)
            response.set_cookie('username', user.username, 60 * 60 * 24 * 14)
            merge_cart_cookie_to_redis(request, response)
            return response

    def post(self, request):
        """
        请求里面有里面有返回生成的sign_openid
        绑定未用QQ登陆过的用户
        两种情况：
        1.有美多账号的
            绑定原有美多账号

        2.没有美多账号的
            快速注册账号
        """
        # 接受表单信息：手机号，密码，短信验证码 opeid 短信验证码前段会自动请求之前写好的模块
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        sign_openid = request.POST.get('openid')

        # 校验信息
        if all([mobile, password, sms_code, sign_openid]) is False:
            return HttpResponse('参数不齐')

        # 正则匹配成功返回一个对象失败返回None 手机
        if re.match(r'^1[3-9]\d{9}$', mobile) is None:
            return HttpResponse("手机号不对")
        # 密码

        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return HttpResponse("密码格式不对")
        # 短信
        # 创建连接
        cn = get_redis_connection('verify_code')

        # 获取redis中的验证码
        sms_code_server = cn.get('sms_%s' % mobile)

        # 检查短信验证码是否过期
        if sms_code_server is None:
            return HttpResponse('验证码过期')

        # 立刻删掉验证码释放资源或等待下次验证
        cn.delete('sms_%s' % mobile)

        # 匹配
        sms_code_server = sms_code_server.decode()
        if sms_code != sms_code_server:
            return HttpResponse('验证码输入有误请重新输入')

        # #openid 解密
        openid = check_openid_signature(sign_openid)

        # 为什么校验openid不用像短信验证码对比存在redis数据库
        if openid is None:
            return HttpResponseForbidden('openid不存在')
        #
        """
        通过之后两种情况
            1用户注册过美多账号给他绑定QQ登录账号
                查询数据库
                绑定
                登录返回来源界面
            2用户没有美多账号用QQ给他快速注册一个绑定QQ使用
                没有查到
                后台给他注册一个
                返回登录界面
        """
        # 报错说明查不到
        try:

            user = User.objects.get(mobile=mobile)

        except:
            # 如果查询不到,说明是没有注册过的用户,就创建一个新美多用户, 再和openid绑定
            # 这个用户会存在一个问题他的用户名是手机号和其他用户格式不一样

            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        # else没有错误执行
        else:
            # 如果查询到,说明是已注册用户,校验旧用户的密码是否正确那么openid就和已注册用户直接绑定
            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '你有账号注册的用户名或密码错误'})

        # 无论新老用户,都放心大胆的和openid进行绑定
        # oauth的方法绑定qq和原来用户
        OAuthQQUser.objects.create(openid=openid, user=user)

        # 保持绑定
        login(request, user)

        # 创建响应对象、 查询字符串传参

        response = redirect(request.GET.get('stat', '/'))
        # 构建cookie章台保持闭环
        response.set_cookie("username", user.username, max_age=60 * 60 * 24 * 14)
        # 重定向
        logger.info(response)

        merge_cart_cookie_to_redis(request, response)
        return response


class SINAOAuth(View):
    """微博登陆url"""

    def get(self, request):
        """传给前段微博登录url"""
        # 获取查询参数
        next = request.GET.get('next', '/')

        # 用了weibo包,改成自定义 的SDK实质是自己发送网络请求接受参数
        # 请求路径

        # 实例化连接对象
        client = APIClient(app_key=settings.APP_KEY,
                           app_secret=settings.APP_SECRET,
                           redirect_uri=settings.WEIBO_REDIRECT_URI,
                           )

        # 调用它里面的get_qq_url方法得到拼接好的QQ登录url

        login_url = client.get_authorize_url()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class SINAOAuthView(View):
    """处理WEIBO登陆状态"""

    def get(self, request):
        """OAuth 认证过程"""
        # 获取参数的code
        code = request.GET.get('code')
        logger.info(code)
        # 校验code
        if code is None:
            return HttpResponse('错误')

        # 实例化连接对象
        client = APIClient(app_key=settings.APP_KEY,
                           app_secret=settings.APP_SECRET,
                           redirect_uri=settings.WEIBO_REDIRECT_URI,
                           )
        try:
            result = client.request_access_token(code)
            logger.info(result)
            access_token = result.access_token
            uid = result.uid


        except:
            logger.info('认证失败')
            return HttpResponse('认证失败uid')

        try:  # 得不到报错try 一下
            weibo_model = OAuthSINAUser.objects.get(openid=uid)  # 匹配一个微博用户对象

        except:

            uid = generate_openid_signature(uid)
            return render(request, 'oauth_callback.html', {"openid": uid})
        else:

            user = weibo_model.user

            login(request, user)

            response = redirect(request.GET.get('state', '/'))

            response.set_cookie('username', user.username, 60 * 60 * 24 * 14)
            merge_cart_cookie_to_redis(request, response)
            return response

    def post(self, request):
        """

        绑定未用WEIBO登陆过的用户
        两种情况：
        1.有美多账号的
            绑定原有美多账号

        2.没有美多账号的
            快速注册账号
        """

        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        sign_openid = request.POST.get('openid')

        if all([mobile, password, sms_code, sign_openid]) is False:
            return HttpResponse('参数不齐')

        # 正则匹配成功返回一个对象失败返回None 手机
        if re.match(r'^1[3-9]\d{9}$', mobile) is None:
            return HttpResponse("手机号不对")

        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return HttpResponse("密码格式不对")

        cn = get_redis_connection('verify_code')

        sms_code_server = cn.get('sms_%s' % mobile)

        if sms_code_server is None:
            return HttpResponse('验证码过期')

        cn.delete('sms_%s' % mobile)

        sms_code_server = sms_code_server.decode()
        if sms_code != sms_code_server:
            return HttpResponse('验证码输入有误请重新输入')

        uid = check_openid_signature(sign_openid)

        if uid is None:
            return HttpResponseForbidden('uid不存在')

        try:

            user = User.objects.get(mobile=mobile)

        except:

            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)

        else:

            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '你有账号注册的用户名或密码错误'})

        OAuthSINAUser.objects.create(openid=uid, user=user)

        login(request, user)

        response = redirect(request.GET.get('stat', '/'))

        response.set_cookie("username", user.username, max_age=60 * 60 * 24 * 14)

        logger.info(response)

        merge_cart_cookie_to_redis(request, response)
        return response


class WEIBO(View):
    # 访问微博授权页面
    def get(self, request):  # 跳转授权页面
        next = request.GET.get('next', '/')

        login_url = 'https://api.weibo.com/oauth2/authorize?client_id=' + settings.APP_KEY + '&client_secret=' + settings.APP_SECRET + '&redirect_uri=' + settings.WEIBO_REDIRECT_URI
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})

# requests 发起网络请求
class WEIBOView(View):
    # 认证接受微博数据
    def get(self, request):  # oauth认证
        code = request.GET.get("code")
        url = "https://api.weibo.com/oauth2/access_token"
        cn = OAuthWB(client_id=settings.APP_KEY, client_key=settings.APP_SECRET,
                     redirect_uri=settings.WEIBO_REDIRECT_URI)
        # requests认证oauth
        dict = cn.get_access_token(code)

        uid = dict.get("uid")
        print(type(uid))
        if uid is None:
            return HttpResponse("认证失败")

        try:  # 得不到报错try 一下
              # 匹配一个微博用户对象

            weibo_model = OAuthSINAUser.objects.get(openid=uid)
            print(type(weibo_model))
        except:
            uid = generate_openid_signature(uid)
            return render(request, 'oauth_callback.html', {"openid": uid})


        user = weibo_model.user

        login(request, user)

        response = redirect(request.GET.get('state', '/'))

        response.set_cookie('username', user.username, 60 * 60 * 24 * 14)
        merge_cart_cookie_to_redis(request, response)
        return response

    def post(self, request):
        """

        绑定未用WEIBO登陆过的用户
        两种情况：
        1.有美多账号的
            绑定原有美多账号

        2.没有美多账号的
            快速注册账号
        """

        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        sign_openid = request.POST.get('openid')
        print(sign_openid)

        if all([mobile, password, sms_code, sign_openid]) is False:
            return HttpResponse('参数不齐')

        # 正则匹配成功返回一个对象失败返回None 手机
        if re.match(r'^1[3-9]\d{9}$', mobile) is None:
            return HttpResponse("手机号不对")

        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return HttpResponse("密码格式不对")

        cn = get_redis_connection('verify_code')

        sms_code_server = cn.get('sms_%s' % mobile)

        if sms_code_server is None:
            return HttpResponse('验证码过期')

        cn.delete('sms_%s' % mobile)

        sms_code_server = sms_code_server.decode()
        if sms_code != sms_code_server:
            return HttpResponse('验证码输入有误请重新输入')

        uid = check_openid_signature(sign_openid)

        if uid is None:
            return HttpResponseForbidden('uid不存在')

        try:

            user = User.objects.get(mobile=mobile)

        except:

            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)

        else:

            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '你有账号注册的用户名或密码错误'})

        OAuthSINAUser.objects.create(openid=uid, user=user)

        login(request, user)

        response = redirect(request.GET.get('stat', '/'))

        response.set_cookie("username", user.username, max_age=60 * 60 * 24 * 14)

        logger.info(response)

        merge_cart_cookie_to_redis(request, response)
        return response