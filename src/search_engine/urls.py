from django.urls import path
from . import views

urlpatterns = [
    path(
        'list/<str:text>/',
        views.SearchEngineListApiView.as_view(),
        name='search_engine_list_api'
    )
]