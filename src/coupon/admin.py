from django.contrib import admin

from .models import Category, Coupon, CouponImage, LineCoupon, FAQ, Rate, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent"]
    list_filter = ["parent", ]
    list_editable = ["parent", ]


class FAQAdmin(admin.ModelAdmin):
    list_display = ["title", "category", ]
    list_filter = ["category"]


class ImageInline(admin.TabularInline):
    model = CouponImage


class CouponAdmin(admin.ModelAdmin):
    list_display = ["title", "business", "created", "expire_date"]
    list_filter = ["business", "category", "created", "expire_date"]
    inlines = [ImageInline, ]


@admin.register(CouponImage)
class CouponImageAdmin(admin.ModelAdmin):
    list_display = ["id", "coupon"]
    # search_fields = ["coupon__title"]
    # autocomplete_fields = ["coupon"]


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
