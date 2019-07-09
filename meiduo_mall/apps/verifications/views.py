import pickle
import base64

from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from random import randint

from users.models import User
from . import constants
from meiduo_mall.libs.captcha.captcha import captcha
# from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils.response_code import RETCODE
import logging
from celery_tasks.sms.tasks import send_sms_code

logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        # 生成图形验证码
        # name唯一标识  image_code_text图形验证码的字符 image_bytes图形验证码bytes
        name, image_code_text, image_bytes = captcha.generate_captcha()
        # 创建redis连接对象  存储图片验证码字符的目的,以后后期验证使用
        redis_conn = get_redis_connection('verify_code')
        # 将图形验证码的字符 存储到redis中 用uuid作为key
        redis_conn.setex(uuid, constants.IMAGE_CODE_REDIS_EXPIRES, image_code_text)
        # 响应 把生成好的图片验证码bytes数据作为响应体响应给前端
        return http.HttpResponse(image_bytes, content_type='image/jpg')


# GET /sms_codes/15312345672/?image_code=5vib&uuid=99f6bc61-1f14-41eb-8f28-253258da20ee
class SMSCodeView(View):
    """发送短信验证码"""

    def get(self, request, mobile):

        # 来发短信之前先判断此手机号有没有在60s之前发过
        # 0. 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 尝试性去获取此手机号是否有发过短信的标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 如果胡提前响应
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

        # 1.接收前端传入的数据
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 2.校验数据
        if all([image_code_client, uuid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        # 2.2 获取redis中的图形验证码
        image_code_server = redis_conn.get(uuid)  # 从redis获取出来的数据都是bytes类型

        # 2.3 把redis中图形验证码删除
        redis_conn.delete(uuid)  # 只让图形验证码使用一次
        # 2.4 判断短信验证码是否过期
        if image_code_server is None:
            return http.HttpResponseForbidden('图形验证码过期')
        # 2.5 注册必须保证image_code_server它不会None再去调用decode
        image_code_server = image_code_server.decode()
        # 2. 6 判断用户输入验证码是否正确 注意转换大小写
        if image_code_client.lower() != image_code_server.lower():
            return http.HttpResponseForbidden('图形验证码输入有误')

        # 3. 随机生成一个6位数字作为验证码
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)

        # redis管道技术
        pl = redis_conn.pipeline()
        # 将短信验证码存储到redis,以备后期注册时校验
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 向redis多存储一个此手机号已发送过短信的标记,此标记有效期60秒
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道
        pl.execute()

        # 给当前手机号发短信
        # CCP().send_template_sms(要收短信的手机号, [短信验证码, 短信中提示的过期时间单位分钟], 短信模板id)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        send_sms_code.delay(mobile, sms_code)  # 生产任务
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信验证码成功'})


class FindPasswordView(View):

    def get(self, request, username):

        uuid = request.GET.get('image_code_id')


        try:
            user = User.objects.get(username=username)
            mobile = user.mobile
        except User.DoesNotExist:
            return http.HttpResponse(status=404)

        redis_conn = get_redis_connection('verify_code')
        # 尝试性去获取此手机号是否有发过短信的标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 如果胡提前响应
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

        # 1.接收前端传入的数据
        image_code_client = request.GET.get('text')

        # 2.校验数据
        if all([image_code_client, uuid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        # 2.2 获取redis中的图形验证码
        image_code_server = redis_conn.get(uuid)  # 从redis获取出来的数据都是bytes类型

        # 2.3 把redis中图形验证码删除
        redis_conn.delete(uuid)  # 只让图形验证码使用一次
        # 2.4 判断短信验证码是否过期
        if image_code_server is None:
            return http.HttpResponseForbidden('图形验证码过期')
        # 2.5 注册必须保证image_code_server它不会None再去调用decode
        image_code_server = image_code_server.decode()
        # 2. 6 判断用户输入验证码是否正确 注意转换大小写
        # print(image_code_client)
        # print(image_code_server)
        if image_code_client.lower() != image_code_server.lower():
            return http.HttpResponse(status=400)

        access_token = base64.b64encode(pickle.dumps(user.id)).decode()
        # print(type(access_token))
        # print(access_token)

        # 取出手机号码中间四位
        list = mobile[3:7]
        # 星号替换中间四位号码
        mobile = mobile.replace(list,'****')

        # 返回的Json数据中，mobile加密显示
        return http.JsonResponse({"mobile": mobile, 'access_token': access_token})


class FindSMSCodeView(View):

    def get(self, request):
        access_token = request.GET.get('access_token')

        try:
            user_id = pickle.loads(base64.b64decode(access_token.encode()))
            user = User.objects.get(id=user_id)
            mobile = user.mobile
        except:
            return http.HttpResponseForbidden('无效的access_token')

        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)

        redis_conn = get_redis_connection('verify_code')
        # redis管道技术
        pl = redis_conn.pipeline()
        # 将短信验证码存储到redis,以备后期注册时校验
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 向redis多存储一个此手机号已发送过短信的标记,此标记有效期60秒
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        # 执行管道
        pl.execute()

        # 给当前手机号发短信
        # CCP().send_template_sms(要收短信的手机号, [短信验证码, 短信中提示的过期时间单位分钟], 短信模板id)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        send_sms_code.delay(mobile, sms_code)  # 生产任务
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信验证码成功'})


class VerificationSMSCodeView(View):

    def get(self, request, username):
        sms_code = request.GET.get('sms_code')
        # access_token = request.GET.get('access_token')

        try:
            # user_id = pickle.loads(base64.b64decode(access_token.encode()))
            user = User.objects.get(username=username)
            mobile = user.mobile
        except:
            return http.HttpResponse(status=404)

        redis_conn = get_redis_connection('verify_code')
        # 获取reids中短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden('短信验证码已过期')
        # 删除reids中已被使用过的短信验证
        redis_conn.delete('sms_%s' % mobile)
        # 由bytes转换为str
        sms_code_server = sms_code_server.decode()
        # 判断用户输入的短信验证码是否正确
        if sms_code != sms_code_server:
            return http.HttpResponse(status=400)

        access_token = base64.b64encode(pickle.dumps(user.username)).decode()

        return http.JsonResponse({'user_id': user.id, 'access_token': access_token})








