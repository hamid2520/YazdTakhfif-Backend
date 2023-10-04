from rest_framework.generics import ListAPIView
from rest_framework.mixins import RetrieveModelMixin


class ListRetrieveAPIView(RetrieveModelMixin, ListAPIView):
    pass

