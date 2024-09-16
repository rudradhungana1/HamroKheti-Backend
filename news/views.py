# news/views.py
from django.core.management import call_command
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.combine_error_message import combine_error_messages
from .models import News, VegetableMarget
from .serializers import NewsSerializer, VegetableMarketSerializer


class NewsViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = News.objects.all().order_by('-created_at')
        serializer = NewsSerializer(queryset, many=True)
        return Response({
            'status': 'SUCCESS',
            'message': 'DATA RETRIEVED SUCCESSFULLY',
            'data': serializer.data
        })

    @action(methods=['PATCH', 'POST'], detail=True, url_path='update-news')
    def update_news(self, request, pk=None):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'admin':
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authorized'},
                                status=status.HTTP_401_UNAUTHORIZED)
            news = News.objects.get(pk=pk)
            serializer = NewsSerializer(news, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'SUCCESS', 'data': serializer.data,'message': 'UPDATED SUCCESSFULLY'})
            else:
                return Response({'status': 'FAILURE', 'data': None,'message': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'FAILURE', 'data': None,'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            news = News.objects.get(pk=pk)
            serializer = NewsSerializer(news)
            return Response({
                "message": "DATA RETRIEVED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": serializer.data
            })
        except News.DoesNotExist:
            return Response({
                "message": "DATA NOT FOUND",
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    # /news/news/scrape
    @action(methods=['GET'], detail=False, url_path='scrape')
    def get_list(self, request):
        try:
            call_command('scrape_news')
            return Response({'status': 'SUCCESS', 'message': 'Scraping completed successfully'})
        except Exception as e:
            return Response({'status': 'FAILURE','message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['DELETE'], detail=True, url_path='delete-news')
    def delete_news(self, request, pk=None):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'admin':
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authorized'},
                                status=status.HTTP_400_BAD_REQUEST)
            news = News.objects.get(pk=pk)
            news.delete()
            return Response({'status': 'SUCCESS', 'message': 'News Deleted Successfully'}, status=200)
        except Exception as e:
            return Response({'status': 'FAILURE', 'data': None,
                             'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['POST'], detail=False, url_path='add-news')
    def add_news(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'admin':
                return Response({'status': 'FAILURE', 'data': None,'message': 'You are not authorized'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = NewsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(source='admin')
                return Response({'status': 'SUCCESS', 'message': 'News Added Successfully !', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'status': 'FAILURE', 'message': combine_error_messages(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VegetableMarketViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = VegetableMarget.objects.all()
        serializer = VegetableMarketSerializer(queryset, many=True)
        return Response({
            'status': 'SUCCESS',
            'message': 'DATA RETRIEVED SUCCESSFULLY',
            'data': serializer.data
        })


    @action(methods=['GET'], detail=False, url_path='scrape')
    def get_list(self, request):
        try:
            call_command('scrap_veg_market')
            return Response({'status':'SUCCESS', 'message': 'Scraping completed successfully'})
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)