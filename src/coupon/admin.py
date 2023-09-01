from django.contrib import admin

from src.coupon.models import Category, Coupon, LineCoupon, FAQ


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent", "level"]
    list_filter = ["parent", "level"]
    list_editable = ["parent", "level"]


class FAQAdmin(admin.ModelAdmin):
    list_display = ["title", "category",]
    list_filter = ["category"]


class CouponAdmin(admin.ModelAdmin):
    list_display = ["title", "business", "created", "expire_date"]
    list_filter = ["business", "category", "created", "expire_date"]


class LineCouponAdmin(admin.ModelAdmin):
    list_display = ["title", "coupon", "is_main", "offer_percent", "price", "final_price", "count", "bought_count",
                    "rate"]
    list_filter = ["coupon", "is_main"]
    list_editable = ["offer_percent", "is_main", "price", "count", "rate"]
    readonly_fields = ["final_price", "bought_count", ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(LineCoupon, LineCouponAdmin)
