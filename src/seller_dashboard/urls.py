from django.urls import path
from .views import UserCommentList

urlpatterns = [
    path('user-comment-list/', UserCommentList.as_view(), name='user_comment_list')
]