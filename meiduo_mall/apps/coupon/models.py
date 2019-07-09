from django.db import models

# Create your models here.

from meiduo_mall.utils.models import BaseModel
from users.models import User


class Couponcard(BaseModel):
    coupon_id = models.CharField(max_length=20, verbose_name="优惠券编号")

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='获取优惠券用户')

    class Meta:
        db_table = "tb_coupon"
        verbose_name = "优惠券列表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.coupon_id
