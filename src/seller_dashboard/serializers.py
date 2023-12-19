from rest_framework import serializers

from src.coupon.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    coupon = serializers.SlugRelatedField("slug", read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
    def get_user_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
