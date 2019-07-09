from django.conf.urls import url

from coupon import views

urlpatterns = [

    url(r'^coupon/$', views.CouponPaymentView.as_view()),
]