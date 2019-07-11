from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.home_serializer import GoodsSerializer
from users.models import User


# 总用户数量
class UserTotalView(APIView):
    # 只允许管理员账号请求
    permissions_user = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        date_now = date.today()
        # 获取全部用户数量
        count = User.objects.all().count()
        return Response({
            'date': date_now,
            'count': count
        })


# 日增用户量
class UserDayCountView(APIView):
    permissions_user = [IsAdminUser]

    def get(self, request):
        date_now = date.today()
        # 获取今天新增用户数量
        count = User.objects.filter(date_joined__gte=date_now).count()
        return Response({
            'date': date_now,
            'count': count
        })


# 日活量
class UserActiveCountView(APIView):
    permissions_user = [IsAdminUser]

    def get(self, request):
        date_now = date.today()
        # 今日登录的用户数量
        count = User.objects.filter(last_login__gte=date_now).count()
        return Response({
            'date': date_now,
            'count': count
        })


# 今日下单量
class UserOrderCountView(APIView):
    permissions_user = [IsAdminUser]

    def get(self, request):
        date_now = date.today()
        # 获取今天下单的用户
        order_qs = User.objects.filter(orderinfo__create_time__gte=date_now)
        # 去除重复用户
        count = len(set(order_qs))
        return Response({
            'date': date_now,
            'count': count
        })


# 月新增用户量
class UserMonthCountView(APIView):
    permissions_user = [IsAdminUser]

    def get(self, request):
        date_now = date.today()
        # 以date_now向前推移29天获取日期
        start_date = date_now - timedelta(29)
        # 创数据列表
        data_list = []
        # 循环遍历30天
        for i in range(30):
            # 获取循环的当天时间
            index_date = start_date + timedelta(days=i)
            # 获取循环下一天时间
            cur_date = start_date + timedelta(days=i + 1)
            # 取当前天数到下一天时间的全部新增用户
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()
            # 每天情况添加到data_list中
            data_list.append({
                'date': index_date,
                'count': count
            })
        return Response(data_list)


# 日分类商品访问量
class GoodsDayView(APIView):
    def get(self, request):
        now_date = date.today()
        # 获取今天商品访问数据
        data = GoodsVisitCount.objects.filter(date=now_date)
        # 序列化
        ser = GoodsSerializer(data, many=True)
        # 响应
        return Response(ser.data)
