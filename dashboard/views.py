from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from news.models import News, VegetableMarget
from orders.models import Order
from products.models import Product
from users.models import User


# Create your views here.
@api_view(['GET'])
def dashboard(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({
              'message': 'You are not authenticated',
              'status': 'ERROR',
            }, status=401)
        if not user.is_superuser or not user.user_role == 'admin':
            return Response({
             'message': 'You are not authorized',
             'status': 'ERROR',
            }, status=403)

        total_users = User.objects.all().count()
        total_products = Product.objects.all().count()
        total_orders = Order.objects.all().count()
        total_admins = User.objects.filter(user_role='admin').count()
        total_farmer = User.objects.filter(user_role='farmer').count()
        total_partner = User.objects.filter(user_role='partner').count()
        total_customer = User.objects.filter(user_role='normal_user').count()
        total_news = News.objects.all().count()
        total_veg_market = VegetableMarget.objects.all().count()

        return Response({
            'status': 'SUCCESS',
            'message': 'Data retrieved successfully',
            'data': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_farmers': total_farmer,
                'total_partners': total_partner,
                'total_admins': total_admins,
                'total_customers': total_customer,
                'total_news': total_news,
                'total_veg_market': total_veg_market,
            }
        }, status=200)
    except Exception as e:
        return Response({
           'message': str(e),
           'status': 'FAILURE',
        }, status=400)