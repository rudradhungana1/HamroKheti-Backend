from django.db.models import Avg
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from utils.combine_error_message import combine_error_messages
from utils.upload_image import upload_image
from .models import Product, Comment, Review, Reply
from .serializers import ProductSerializer, CommentSerializer, ReviewSerializer, ReviewCheckSerializer, ReplySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category', 'location', 'name']
    permission_classes = [IsAuthenticated]

    def create(self, request, **kwargs):
        try:
            user = request.user
            if user:
                if user.user_role == 'farmer':
                    is_profile = hasattr(
                        user, 'farmer_profile'
                    )
                    if is_profile:
                        verified = user.farmer_profile.is_verified
                        percentage = user.farmer_profile.farmer_profile_percentage
                        if not verified:
                            return Response({'status': 'FAILURE', 'message': f"You are not verified to create "
                                                                             f"products. You have to fill your profile "
                                                                             f"first"
                                                                             f"{percentage} % is filled now"},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'status': 'FAILURE', 'message': 'You need to fill your profile first'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    base64_image = request.data.get('product_image')
                    image_url = upload_image(base64_image, '/products')
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save(user=user, image=image_url)
                        return Response({
                            'message': 'Product added successfully',
                            'status': 'SUCCESS',
                            'data': serializer.data,
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'status': 'FAILURE', 'message': serializer.errors},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'status': 'FAILURE', 'message': 'You are not authorized'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(
            {
                'message': 'DATA RETRIEVED SUCCESSFULLY',
                'status': 'SUCCESS',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['GET'])
    def my_products(self, request):
        """
        Retrieve products listed by the authenticated farmer (user).
        """
        user = request.user

        if user and user.user_role == 'farmer':
            products = Product.objects.filter(user=user)
            serializer = self.get_serializer(products, many=True)
            return Response(
                {
                    'message': 'DATA RETRIEVED SUCCESSFULLY',
                    'status': 'SUCCESS',
                    'data': serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    'message': 'Authentication Required',
                    'status': 'FAILURE',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def update(self, request, pk=None, **kwargs):
        try:
            user = request.user
            if not user:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.user_role == 'farmer':
                return Response({'status': 'FAILURE', 'message': 'You are not authorized'},
                                status=status.HTTP_400_BAD_REQUEST)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                product_image = request.data.get('product_image')
                if product_image:
                    image_url = upload_image(product_image, '/products')
                    serializer.save(image=image_url)
                serializer.save()
                return Response({'status': 'SUCCESS', 'message': 'UPDATED SUCCESSFULLY', 'data': serializer.data})
            else:
                return Response({'status': 'FAILURE', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, **kwargs):
        try:
            user = request.user
            if not user:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)

            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'SUCCESS',
                'message': 'Data Retrieve Successfully',
                'data': serializer.data,
            })

        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk=None):
        try:
            user = request.user
            if not user:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.user_role == 'farmer' or not user.user_role == 'admin':
                return Response({'status': 'FAILURE', 'message': 'You are not authorized'},
                                status=status.HTTP_400_BAD_REQUEST)
            instance = Product.objects.get(pk=pk)
            instance.delete()
            return Response({
                'status': 'SUCCESS',
                'message': 'DELETED SUCCESSFULLY'
            }, status=200)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        comments = Comment.objects.prefetch_related('replies').all().order_by('-created_at')
        return comments

    @action(methods=['POST'], detail=False, url_path='post-comment')
    def post_comment(self, request):
        try:
            serializer = self.serializer_class(data=request.data)

            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(
                    {
                        'data': serializer.data,
                        'message': 'Comment posted successfully',
                        'status': 'SUCCESS',
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'message': combine_error_messages(serializer.errors),
                    'status': 'FAILURE'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'message': str(e),
                    'status': 'FAILURE'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['POST'], detail=True, url_path='give-reply')
    def give_reply(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)

            reply_text = request.data.get('text')
            if not reply_text:
                return Response({'status': 'FAILURE', 'message': 'Reply text is required'},
                                status=status.HTTP_400_BAD_REQUEST)

            reply = Reply.objects.create(user=request.user, comment=comment, text=reply_text)
            serializer = ReplySerializer(reply)
            return Response(
                {
                    'data': serializer.data,
                    'message': 'Reply posted successfully',
                    'status': 'SUCCESS',
                },
                status=status.HTTP_201_CREATED
            )
        except Comment.DoesNotExist:
            return Response({'status': 'FAILURE', 'message': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)
            comments = self.get_queryset()
            serializer = self.serializer_class(comments, many=True)
            return Response(
                {
                    'data': serializer.data,
                    'message': 'DATA RETRIEVED SUCCESSFULLY',
                    'status': 'SUCCESS',
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['POST'], detail=False, url_path='get-product-review')
    def get_all_reviews_by_product(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'FAILURE', 'message': 'You must be authenticated'},
                                status=status.HTTP_400_BAD_REQUEST)

            product = request.data.get('product')
            if not product:
                return Response({'status': 'FAILURE', 'message': 'Product data is required'},
                                status=status.HTTP_400_BAD_REQUEST)

            reviews = self.queryset.filter(product=product)
            serializer = self.serializer_class(reviews, many=True)
            return Response(
                {
                    'data': serializer.data,
                    'message': 'DATA RETRIEVED SUCCESSFULLY',
                    'status': 'SUCCESS',
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='check-review')
    def check_review(self, request):
        serializer = ReviewCheckSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            user = request.user

            if user.is_authenticated:
                has_ordered = Order.objects.filter(customer=user, order_items__product_id=product_id,
                                                   status__in=['completed', 'delivered']).exists()
                if has_ordered:
                    has_reviewed = self.queryset.filter(product_id=product_id, user=user).exists()
                    message = "Your review has been reviewed" if has_reviewed else "Your review has not been reviewed"
                    if has_ordered and not has_reviewed:
                        return Response({'status': 'SUCCESS', 'message': message,
                                         'data': {'to_review': True, 'has_reviewed': has_reviewed,
                                                  'has_ordered': has_reviewed}})
                else:
                    return Response({'status': 'FAILURE', 'message': 'You must have to complete your order first',
                                     'data': {'has_reviewed': False, 'has_ordered': has_ordered, 'to_review': False}})
            else:
                return Response({'status': 'FAILURE', 'message': 'Authentication required'}, status=401)
        return Response(serializer.errors, status=400)

    @action(methods=['post'], detail=False, url_path='add-review')
    def add_review(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = request.user
                product_id = serializer.validated_data['product'].id
                if user.orders.filter(order_items__product_id=product_id, status='completed').exists():
                    serializer.save(user=request.user)
                    self.process_order_completion(serializer.validated_data['product'])
                    return Response({
                        'status': 'SUCCESS',
                        'message': 'Successfully added a review to the product',
                        'data': serializer.data
                    }, status=201)
                else:
                    return Response({
                        'status': 'FAILURE',
                        'message': 'You must complete an order for this product before reviewing it.'
                    }, status=400)

            return Response({
                'status': 'FAILURE',
                'message': combine_error_messages(serializer.errors)
            }, status=400)
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def process_order_completion(self, product):
        try:
            orders = Order.objects.filter(order_items__product=product, status='completed', completed=False)
            for order in orders:
                order.completed = True
                order.save()
                reviews = Review.objects.filter(product=product)
                total_ratings = reviews.count()
                average_rating = reviews.aggregate(Avg('rating_value'))['rating_value__avg']
                product.total_ratings = total_ratings
                product.average_rating = average_rating or 0
                product.save()
        except Exception as e:
            return Response({
                'status': 'FAILURE',
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
