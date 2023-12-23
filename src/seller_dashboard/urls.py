from django.urls import path

from .views import SellerDashboardAPIView, SellerDashboardCouponsAPIView, UserCommentList

urlpatterns = [
    path('recently-sold-coupons/', SellerDashboardCouponsAPIView.as_view(), name='recently_sold_coupons'),
    path('user-comment-list/', UserCommentList.as_view(), name='user_comment_list'),
    path('', SellerDashboardAPIView.as_view(), name='seller_dashboard'),
]
