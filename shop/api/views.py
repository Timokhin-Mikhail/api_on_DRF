import operator
from datetime import timezone
from functools import reduce
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.db.models.constants import LOOKUP_SEP
from rest_framework import status
from rest_framework.compat import distinct
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from api.serializers import ProfileSerializer, CategorySerializer, AvatarSerializer, PasswordSerializer, TagSerializer,\
    Paymenterializer, ProductsSerializer, ProductSerializer, ReviewSerializer, BasketProductsSerializer,\
    BasketChangesSerializer, SalesSerializer, OrderSerializer
from django.db.models import Value, CharField, Count, Avg
from django.db.models.functions import Concat, Round, Coalesce
from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.utils.serializer_helpers import ReturnList
from api.models import Profile, Category, Tag, Payment, Product, Review, Baskets, Sales, Order


class ProfileList(APIView):

    def get(self, request):
        user = Profile.objects.select_related('user').filter(user=request.user)
        serializer = ProfileSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = Profile.objects.select_related('user').get(user=request.user)
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetAvatar(APIView):
    def post(self, request):
        user = Profile.objects.select_related('user').get(user=request.user)
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPassword(APIView):

    def post(self, request):
        user = Profile.objects.select_related('user').get(user=request.user)
        serializer = PasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryList(APIView):

    def get(self, request):
        category = Category.objects.filter(maincategories=None).annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()))
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CreatePaymentViewSet(CreateModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = Paymenterializer


def myf(num):
    if num is None:
        return 0
    else:
        return num


class PaginationProduct(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'

    def get_paginated_response(self, data: ReturnList):
        data = [[d] for d in data]

        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class ProductsViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.prefetch_related('reviews').all().\
        annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                 rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0))
    serializer_class = ProductsSerializer


class MyOrdering(OrderingFilter):

    def get_valid_fields(self, queryset, view, context={}):
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)
        valid_fields = [
                (item, item) if isinstance(item, str) else item
                for item in valid_fields
            ]

        return valid_fields

    def remove_invalid_fields(self, queryset, fields, view, request):
        valid_fields = [item[0] for item in self.get_valid_fields(queryset, view, {'request': request})]

        if not (request.query_params.get('sortType', False) == 'inc'):
            fields = ['-'+field for field in fields]

        def term_valid(term):
            if term.startswith("-"):
                term = term[1:]
            return term in valid_fields

        return [term for term in fields if term_valid(term)]


class ProductFilter(SearchFilter):

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        conditions = []
        if (not search_fields or not search_terms) and not request.query_params.get('category', False):
            return queryset
        elif request.query_params.get('category', False):
            queries = [
                Q(**{LOOKUP_SEP.join(['category__id', 'iexact']): request.query_params.get('category', False)})
            ]
            conditions.append(reduce(operator.and_, queries))

        base = queryset
        if search_fields and search_terms:
            orm_lookups = [
                self.construct_search(str(search_field))
                for search_field in search_fields
            ]

            for search_term in search_terms:
                queries = [
                    Q(**{orm_lookup: search_term})
                    for orm_lookup in orm_lookups
                ]
                conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            queryset = distinct(queryset, base)
        return queryset


# class ProductWithIdFilter(SearchFilter):
#
#     def filter_queryset(self, request, queryset, view):
#         search_fields = self.get_search_fields(view, request)
#         search_terms = self.get_search_terms(request)
#         conditions = []
#         queries = [Q(**{LOOKUP_SEP.join(['category__id', 'iexact']): str(view.kwargs['id'])})]
#         conditions.append(reduce(operator.and_, queries))
#         base = queryset
#         if search_fields and search_terms:
#             orm_lookups = [
#                 self.construct_search(str(search_field))
#                 for search_field in search_fields
#             ]
#
#             for search_term in search_terms:
#                 queries = [
#                     Q(**{orm_lookup: search_term})
#                     for orm_lookup in orm_lookups
#                 ]
#                 conditions.append(reduce(operator.or_, queries))
#
#         queryset = queryset.filter(reduce(operator.and_, conditions))
#
#         if self.must_call_distinct(queryset, search_fields):
#             queryset = distinct(queryset, base)
#         return queryset


class ProductsCatalogViewSet(ProductsViewSet):
    pagination_class = PaginationProduct
    filter_backends = [ProductFilter, MyOrdering]
    search_fields = ['title']
    ordering_fields = ['rating', 'price', 'reviews', 'date']
    ordering = ['-date']


class ProductsCatalogWithIdViewSet(ProductsViewSet):
    pagination_class = PaginationProduct
    filter_backends = [ProductFilter, MyOrdering]
    search_fields = ['title']
    ordering_fields = ['rating', 'price', 'reviews', 'date']
    ordering = ['-date']

    def get_queryset(self):
        products =Product.objects.prefetch_related('reviews').filter(category=self.request.parser_context['kwargs']['id']). \
            annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                     rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0))

        return products


class ProductsPopularViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all().annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                                              rev_c=Count('reviews'),
                                              rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0)).\
        order_by('-rev_c', '-rating')
    serializer_class = ProductsSerializer


class ProductsLimitedViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(limited=True).\
        annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                 rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0))
    serializer_class = ProductsSerializer


class ProductsBannersViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(on_banner=True).\
        annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                 rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0))
    serializer_class = ProductsSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField()),
                                        rating=Coalesce(Round(Avg('reviews__rate'), 1), 0.0))
    serializer_class = ProductSerializer


class CreateReviewViewSet(CreateModelMixin, GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class BasketView(APIView):

    def get_products(self, request):
        try:
            products = Baskets.objects.filter(user=request.user).select_for_update('product').\
                prefetch_related('product__reviews')
            return products
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        products = self.get_products(request)
        serializer = BasketProductsSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = BasketChangesSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.filter(pk=serializer.data['id']).first()
            basket = Baskets.objects.filter(user=request.user, product= product).first()
            if basket:
                basket.prod_count = basket.prod_count + serializer.data['count']
                basket.price_mult_count = basket.prod_count * product.price
                basket.save(update_fields=['prod_count', 'price_mult_count'])
                products = self.get_products(request)
                serializer = BasketProductsSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif product:
                price = serializer.data['count'] * product.price
                Baskets.objects.create(product=product, user=request.user, prod_count=serializer.data['count'],
                                       price_mult_count=price)
                products = self.get_products(request)
                serializer = BasketProductsSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        serializer = BasketChangesSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.filter(pk=serializer.data['id']).first()
            basket = Baskets.objects.filter(user=request.user, product= product).first()
            if basket:
                new_count = basket.prod_count - serializer.data['count']
                if new_count > 0:
                    basket.prod_count = new_count
                    basket.price_mult_count = basket.prod_count * product.price
                    basket.save(update_fields=['prod_count', 'price_mult_count'])
                else:
                    basket.delete()
                products = self.get_products(request)
                serializer = BasketProductsSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesViewSet(ReadOnlyModelViewSet):
    queryset = Sales.objects.prefetch_related('product').all()
    serializer_class = SalesSerializer


class MyModelMixin(CreateModelMixin):
    def create(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OrderViewSet(RetrieveAPIView, MyModelMixin):
    queryset = Order.objects.prefetch_related('products').all()
    serializer_class = OrderSerializer


class OrderListViewSet(ListAPIView, MyModelMixin):
    queryset = Order.objects.prefetch_related('products').all()
    serializer_class = OrderSerializer


class LastActiveOrderViewSet(APIView):

    def get(self, request):
        order = Order.objects.filter(user=request.user, active=True).prefetch_related('products').order_by('-createdAt').first()  #\
        print(order)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
