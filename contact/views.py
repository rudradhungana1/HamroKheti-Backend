from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contact.models import Contact
from contact.serializers import ContactSerializer


# Create your views here.
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()

    def list(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    "message": "You are not authenticated to perform this action",
                    "status": "FAILURE",
                }, status=401)

            if not request.user.user_role == 'admin':
                return Response({
                    "message": "You are not authorized to perform this action",
                    "status": "FAILURE",
                }, status=403)

            queryset = Contact.objects.all()
            serializer = ContactSerializer(queryset, many=True)
            return Response({
                'status': 'SUCCESS',
                'message': 'DATA RETRIEVED SUCCESSFULLY',
                'data': serializer.data
            }, status=200)
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e)
            }, status=500)

    @action(methods=['POST'], detail=False, url_path='create')
    def create_contact(self, request):
        try:
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'SUCCESS',
                    'message': 'Contact saved successfully',
                    'data': serializer.data
                }, status=201) 
            else:
                return Response({
                    'status': 'FAILURE',
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=400) 
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e)
            }, status=500) 