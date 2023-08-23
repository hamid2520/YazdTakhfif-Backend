from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404

from .models import Business
from .serializers import BusinessSerializer


class BusinessListApiView(ListCreateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def create(self, request, *args, **kwargs):
        serializer = BusinessSerializer(data=request.data)
        user = Business.objects.filter(user__id=request.user.pk)
        serializer.is_valid(raise_exception=True)
        if not user.exists():
            serializer.validated_data["user"] = request.user
            serializer.save(**serializer.validated_data)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        errors = serializer.errors
        errors["user"] = ["A business with your user_id exists!", ]
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessDetailApiView(RetrieveUpdateDestroyAPIView):
    queryset = Business.objects.all()
    lookup_field = "slug"
    serializer_class = BusinessSerializer
