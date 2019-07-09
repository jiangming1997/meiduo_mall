

from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import GoodsCategory, SKU, GoodsVisitCount, IntegralGoods
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderGoods


class ListView(View):

    def get(self, request, category_id, page_num):

        sort = request.GET.get('sort', 'default')
        sort_last = request.GET.get('sort_last',)
        sort_filed = '-create_time'
        if sort == 'price':
            sort_filed = '-price'
        elif sort == 'hot':
            sort_filed = '-sales'
        if sort_last == sort_filed:
            sort_filed = sort_filed[1:]

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('无效的category_id')

        goods_qs = category.sku_set.filter(is_launched=True).order_by(sort_filed)

        cat1 = category.parent.parent
        cat1.url = cat1.goodschannel_set.all()[0].url
        breadcrumb = {'cat1': cat1, "cat2": category.parent, "cat3": category}

        paginator = Paginator(goods_qs, 5)
        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            'categories': get_categories(),  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'sort_filed': sort_filed,
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)


class HotGoodsView(View):

    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('无效的category_id')

        goods_qs = category.sku_set.filter(is_launched=True).order_by('-sales')[:2]

        goods_list = []
        for goods in goods_qs:
            goods_list.append({'id': goods.id, 'name': goods.name, 'price': goods.price, 'default_image_url': goods.default_image.url})

        return http.JsonResponse({'hot_skus': goods_list})


class DetailView(View):

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return render(request, '404.html')
        spu = sku.spu
        # try:
        category = sku.category
        '''spu_spec_qs=[ {name:xxx,
                               spec_options:[{sku_id:
                                               value:}],}


               ]'''
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option.id)

        current_spu_option_dict = {}
        for temp_sku in spu.sku_set.all():
            temp_current_sku_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_current_sku_option_ids = []
            for temp_current_sku_spec in temp_current_sku_spec_qs:
                temp_current_sku_option_ids.append(temp_current_sku_spec.option.id)
            current_spu_option_dict[tuple(temp_current_sku_option_ids)] = temp_sku.id

        spu_spec_qs = spu.specs.order_by('id')
        for index, spu_spec in enumerate(spu_spec_qs):
            spu_spec.spec_options = spu_spec.options.all()
            temp_list = current_sku_option_ids[:]
            for spu_spec_options in spu_spec.spec_options:
                temp_list[index] = spu_spec_options.id
                spu_spec_options.sku_id = current_spu_option_dict.get(tuple(temp_list))

        context = {
            'categories': get_categories(),  # 商品分类
            'breadcrumb': get_breadcrumb(category),  # 面包屑导航
            'sku': sku,  # 当前要显示的sku模型对象
            'category': category,  # 当前的显示sku所属的三级类别
            'spu': spu,  # sku所属的spu
            'spec_qs': spu_spec_qs,  # 当前商品的所有规格数据
        }

        return render(request, 'detail.html', context)


class DetailVisitView(View):

    def post(self, request, category_id):

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('无效的category_id')

        today_date = timezone.now()

        try:
            counts_data = GoodsVisitCount.objects.get(category_id=category_id, date=today_date)
        except GoodsVisitCount.DoesNotExist:
            counts_data = GoodsVisitCount.objects.create(category_id=category_id)

        counts_data.count += 1
        counts_data.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK' })


class GoodsIntegral(View):
    def get(self, request, page_num):

        sort = request.GET.get('sort', 'default')
        sort_last = request.GET.get('sort_last',)
        sort_filed = '-create_time'
        if sort == 'price':
            sort_filed = '-price'
        elif sort == 'hot':
            sort_filed = '-sales'
        if sort_last == sort_filed:
            sort_filed = sort_filed[1:]

        goods_integral_qs = IntegralGoods.objects.all()
        goods_qs = []
        for goods_integral in goods_integral_qs:
            goods_integral.sku.new_price = goods_integral.new_price
            goods_integral.sku.integral = goods_integral.integral
            goods_qs.append(goods_integral.sku)
        # goods_qs = category.sku_set.filter(is_launched=True).order_by(sort_filed)

        # cat1 = category.parent.parent
        # cat1.url = cat1.goodschannel_set.all()[0].url
        # breadcrumb = {'cat1': cat1, "cat2": category.parent, "cat3": category}

        paginator = Paginator(goods_qs, 5)
        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            'categories': get_categories(),  # 频道分类
            # 'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'sort_filed': sort_filed,
            # 'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'goods_integral.html', context)


class CommentView(View):
    def get(self, request, sku_id):
        try:
            order_goods_qs = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)
        except OrderGoods.DoesNotExist:
            return http.HttpResponseForbidden('无效的sku_id')

        comment_list = []

        for order_goods in order_goods_qs:
            if order_goods.is_anonymous:
                order_goods.order.user.username = '*****'

            comment_list.append({
                'comment': order_goods.comment,
                'name': order_goods.order.user.username,
                'score': order_goods.score
            })
        if comment_list == []:
            comment_list.append({
                'comment': '暂无评价',
                'name': '暂无评价',
                'score': 5
            })
        print(comment_list)

        return http.JsonResponse({'comment_list': comment_list})


