from django.contrib import admin

from .models import Category, Coupon, LineCoupon, FAQ, Rate, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent", "level"]
    list_filter = ["parent", "level"]
    list_editable = ["parent", "level"]


class FAQAdmin(admin.ModelAdmin):
    list_display = ["title", "category", ]
    list_filter = ["category"]


class CouponAdmin(admin.ModelAdmin):
    list_display = ["title", "business", "created", "expire_date"]
    list_filter = ["business", "category", "created", "expire_date"]


class LineCouponAdmin(admin.ModelAdmin):
    list_display = ["title", "coupon", "is_main", "offer_percent", "price", "price_with_offer", "count", "sell_count"]
    list_filter = ["coupon", "is_main"]
    list_editable = ["offer_percent", "is_main", "price", "count"]
    readonly_fields = ["price_with_offer", "sell_count", ]


class RateAdmin(admin.ModelAdmin):
    list_display = ["__str__", "coupon", "user", "rate"]
    list_filter = ["user", "coupon"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ["coupon", "user", "parent", "created_at"]
    list_filter = ["coupon", "user", "parent", "created_at"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(LineCoupon, LineCouponAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Comment, CommentAdmin)
