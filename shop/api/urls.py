from django.urls import path, re_path

from api.views import ProfileList, CategoryList, SetNewPassword, SetAvatar, TagViewSet, CreatePaymentViewSet,\
    ProductsCatalogViewSet, ProductsCatalogWithIdViewSet, ProductsPopularViewSet, ProductsLimitedViewSet,\
    ProductsBannersViewSet, ProductViewSet, CreateReviewViewSet, BasketView, SalesViewSet, OrderViewSet,\
    OrderListViewSet, LastActiveOrderViewSet

urlpatterns = [
    re_path(r'^profile/?$', ProfileList.as_view(), name='profile_detail'),
    re_path(r'^categories/?$', CategoryList.as_view(), name='categories_list'),
    re_path(r'^profile/password/?$', SetNewPassword.as_view(), name='set_password'),
    re_path(r'^profile/avatar/?$', SetAvatar.as_view(), name='set_avatar'),
    re_path(r'^tags/?$', TagViewSet.as_view({'get': 'list'}), name='tags'),
    re_path(r'^payment/?$', CreatePaymentViewSet.as_view({'post': 'create'}), name='create_payment'),
    re_path(r'^catalog/?$', ProductsCatalogViewSet.as_view({'get': 'list'}), name='catalog'),
    path('catalog/<int:id>', ProductsCatalogWithIdViewSet.as_view({'get': 'list'}), name='catalog_wit_id'),
    re_path(r'^products/popular/?$', ProductsPopularViewSet.as_view({'get': 'list'}), name='popular'),
    re_path(r'^products/limited/?$', ProductsLimitedViewSet.as_view({'get': 'list'}), name='limited'),
    re_path(r'^banners/?$', ProductsBannersViewSet.as_view({'get': 'list'}), name='on_banners'),
    path('product/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve'}), name='product_detail'),
    path('product/<int:pk>/review', CreateReviewViewSet.as_view({'post': 'create'}), name='create_review'),
    re_path(r'^basket/?$', BasketView.as_view(), name='users_basket'),
    re_path(r'^sales/?$', SalesViewSet.as_view({'get': 'list'}), name='sales_list'),
    re_path(r'^orders/?$', OrderListViewSet.as_view(), name='order_list'),
    re_path(r'^orders/active/?$', LastActiveOrderViewSet.as_view(), name='order_last_active_detail'),
    path('orders/<int:pk>', OrderViewSet.as_view(), name='order_detail'),

]
