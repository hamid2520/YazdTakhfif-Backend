from django.urls import path

from .views import SellerDashboardAPIView,UserCommentList

urlpatterns = [
    path('', SellerDashboardAPIView.as_view(), name='seller_dashboard'),
    path('user-comment-list/', UserCommentList.as_view(), name='user_comment_list')
]
