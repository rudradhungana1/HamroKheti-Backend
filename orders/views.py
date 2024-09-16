import base64
import hashlib
import json
import os
import uuid
import requests
import hashlib
import hmac

from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import Notification
from orders.models import Order
from orders.serializers import OrderSerializer, OrderAdminSerializer
from users.models import UserProfile, PartnerProfile, FarmerProfile
from users.serializers import UserProfileSerializer, PartnerProfileSerializer, FarmerProfileSerializer
from utils.combine_error_message import combine_error_messages


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [filters.OrderingFilter]
    queryset = Order.objects.all().exclude(
                Q(checkout_type='wallet') & Q(payment_type='pending')
            ).order_by('-created_at')


    @action(detail=True, methods=['GET'], url_path='get-customer-info')
    def get_customer_info(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            has_customer = hasattr(order, 'customer')
            if not has_customer:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order does not have a customer'},
                                status=status.HTTP_403_FORBIDDEN)

            customer = UserProfile.objects.get(user=order.customer)
            serializer = UserProfileSerializer(customer, many=False)
            return Response({'status': 'SUCCESS', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'FAILURE', 'data': None, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_path='get-partner-info')
    def get_partner_info(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            has_partner = hasattr(order, 'delivery_partner')
            if not has_partner:
                return Response(
                    {'status': 'FAILURE', 'data': None, 'message': 'Order does not have a delivery partner'},
                    status=status.HTTP_403_FORBIDDEN)

            partner = PartnerProfile.objects.get(user=order.delivery_partner)
            serializer = PartnerProfileSerializer(partner, many=False)
            return Response({'status': 'SUCCESS', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'FAILURE', 'data': None, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT', 'PATCH'], url_path='reject-order')
    def reject_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)

            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'farmer':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None,
                                 'message': 'Order has already been processed ! You cannot reject this order'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been shipped ! '
                                                                               'You cannot reject this order'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'delivered':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been delivered ! '
                                                                               'You cannot reject this order'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'rejected':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been rejected'},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = 'rejected'
            order.save()
            return Response({
                "message": "ORDER REJECTED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH', 'PUT'], url_path='shipped-order')
    def shipped_orders(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)

            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'partner':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)

            if not order.type == 'partner':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Your ordered type is not partner'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been shipped'},
                                status=status.HTTP_403_FORBIDDEN)

            if not order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order is not being'
                                                                               ' processed by farmer yet'},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = 'shipped'
            order.save()
            return Response({
                "message": "ORDER SHIPPED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='get-partner-orders')
    def get_partner_order_list(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'partner':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)
            order = self.queryset.filter(delivery_partner=request.user).order_by('-created_at')
            serializer = OrderAdminSerializer(order, many=True)
            return Response({
                'status': 'SUCCESS',
                'message': 'DATA RETRIEVED SUCCESSFULLY',
                'data': serializer.data
            }, status=200)
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e),
                'data': None
            }, status=400)

    @action(methods=['PUT', 'PATCH'], detail=True, url_path='complete-order')
    def complete_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)

            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'farmer':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)
            if not order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order is not being'
                                                                               ' processed by yet'},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = 'completed'
            order.save()
            return Response({
                "message": "ORDER COMPLETED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH', 'PUT'], url_path='delivered-order')
    def delivered_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)

            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'partner':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)

            if not order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order is not being shipped yet'},
                                status=status.HTTP_403_FORBIDDEN)

            if not order.delivery_partner == request.user:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = 'delivered'
            order.save()
            return Response({
                "message": "ORDER DELIVERED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH', 'PUT'], url_path='processing-order')
    def processing_order(self, request, pk=None):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'farmer':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)

            order = Order.objects.get(pk=pk)

            if order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been processed !'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'cancelled':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been cancelled !'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been shipped !'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'delivered':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Order has already been delivered !'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'rejected':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot process the order while '
                                                                               'it  is already rejected!'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'completed':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot process the order while '
                                                                               'it is already completed!'},
                                status=status.HTTP_403_FORBIDDEN)

            order.status = 'processing'
            order.save()
            return Response({
                "message": "ORDER PROCESSED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='get-farmer-orders')
    def get_farmer_orders(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'farmer':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)
            orders = self.queryset.filter(order_items__product__user=request.user).order_by('-created_at')
            serializer = OrderAdminSerializer(orders, many=True)
            return Response({
                "message": "DATA RETRIEVED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            })

    @action(detail=False, methods=['GET'], url_path='get-all')
    def get_orders(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authenticated'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.user_role == 'admin':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'},
                                status=status.HTTP_403_FORBIDDEN)
            orders = self.queryset
            serializer = OrderAdminSerializer(orders, many=True)
            return Response({
                "message": "DATA RETRIEVED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            })

    @action(methods=['DELETE'], detail=True, url_path='delete')
    def delete_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            if order.customer != request.user:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You are not authorized'
                                                                               ' to delete this order'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None,
                                 'message': 'You cannot delete this order while it is being processed'},
                                status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None,
                                 'message': 'You cannot delete this order while it is being shipped'},
                                status=status.HTTP_400_BAD_REQUEST)

            order.delete()
            return Response({
                "message": "ORDER DELETED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": None
            }, status=200)
        except Exception as e:
            return Response({
                "message": str(e),
                "status": "FAILURE",
                "data": None
            }, status=404)

    @action(detail=True, methods=['PUT'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        try:
            # Retrieve the order
            order = Order.objects.get(pk=pk)

            # Check if the order belongs to the logged-in user
            if order.customer != request.user:
                return Response({'status': 'FAILURE', 'message': 'You are not authorized to cancel this order'},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status == 'cancelled':
                return Response({'status': 'FAILURE', 'message': 'This order is already cancelled'},
                                status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'processing':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot cancel this order '
                                                                               'while it is being processed'},
                                status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'delivered':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot cancel this order '
                                                                               'while it is being delivered'},
                                status=status.HTTP_400_BAD_REQUEST)

            if order.status == "completed":
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot cancel this order '
                                                                               'while it is already completed'},
                                status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'shipped':
                return Response({'status': 'FAILURE', 'data': None, 'message': 'You cannot cancel this '
                                                                               'order while it is being shipped'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Cancel the order
            order.status = 'cancelled'
            order.save()

            return Response({'status': 'SUCCESS', 'message': 'Order cancelled successfully'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'status': 'FAILURE', 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'], url_path='my-orders')
    def my_orders(self, request):
        try:
            user = request.user

            orders = self.get_queryset().filter(customer=user)
            serializer = OrderSerializer(orders, many=True)

            return Response({
                "message": "DATA RETRIEVED SUCCESSFULLY",
                "status": "SUCCESS",
                "data": serializer.data
            })
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='create-esewa-order')
    def create_order_esewa(self, request):
        try:
            # Extract and decode the base64-encoded data
            encoded_data = request.query_params.get('data', '')
            decoded_data = base64.b64decode(encoded_data)

            # Convert the decoded data to JSON
            esewa_response = json.loads(decoded_data)

            # Extract relevant fields from the decoded JSON
            status = esewa_response.get('status')
            transaction_uuid = esewa_response.get('transaction_uuid')

            # Check if the status is 'COMPLETE'
            if status == 'COMPLETE':
                # Update the payout status of the order model
                order = Order.objects.get(transaction_uuid=transaction_uuid)
                order.payment_type = 'complete'
                order.save()
                return Response({'status': 'SUCCESS', 'message': 'Payout Type Status updated successfully'},
                                status=200)
            else:
                return Response({'status': 'FAILURE', 'message': 'Transaction status is not complete'},
                                status=400)
        except Order.DoesNotExist:
            return Response({'status': 'FAILURE', 'message': 'Order not found'},
                            status=404)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=400)

    @action(detail=False, methods=['POST'], url_path='request')
    def create_order(self, request):
        try:
            # Check if the customer is authenticated
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'message': 'Customer is not authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if the customer has a profile
            if not hasattr(request.user, 'profile'):
                return Response({'status': 'FAILURE', 'message': 'Customer profile does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)

            profile = request.user.profile

            # Check if the profile is filled and verified
            if not profile.is_verified:
                return Response({'status': 'FAILURE',
                                 'message': f'Your profile is not verified, {profile.user_profile_percentage}% is '
                                            f'filled'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create order
            checkout_type = request.data.get('checkout_type')

            if checkout_type == 'cash':
                order_serializer = OrderSerializer(data=request.data)
                if order_serializer.is_valid():
                    order_serializer.save(customer=request.user)
                    return Response({
                        "status": "SUCCESS",
                        "type": "cash",
                        "message": "Your order is placed successfully ! Please check your order settings",
                        "data": order_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'status': 'FAILURE', 'message': order_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif checkout_type == "wallet":
                order_serializer = OrderSerializer(data=request.data)
                if order_serializer.is_valid():
                    order_serializer.save(customer=request.user)
                    return Response({
                        "status": "SUCCESS",
                        "type": "wallet",
                        "message": "Redirecting to the esewa wallet url...",
                        "data": order_serializer.data,
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 'FAILURE', 'data': None, 'message': 'Invalid checkout type'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def generate_hmac_signature(data):
    secret_key = os.environ.get('SECRET_KEY')
    hmac_digest = hashlib.sha256(data.encode()).digest()
    hmac_signature = base64.b64encode(hmac_digest).decode()
    return hmac_signature
