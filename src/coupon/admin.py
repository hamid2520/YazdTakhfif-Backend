from django.contrib import admin

from .models import Category, Coupon, CouponImage, LineCoupon, FAQ, Rate, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent"]
    list_editable = ["parent", ]
    search_fields = ["title", ]
    autocomplete_fields = ["parent", ]
    list_filter = ["parent", ]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["title", "category"]
    list_filter = ["category", ]
    search_fields = ["title", "answer", "category__title"]
    autocomplete_fields = ["category", ]


class ImageInline(admin.TabularInline):
    model = CouponImage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["title", "business", "created", "expire_date"]
    list_filter = ["category", "created", "expire_date", "coupon_rate"]
    search_fields = ["title", "business__admin__username"]
    autocomplete_fields = ["business", "category"]
    readonly_fields = ["coupon_rate", "rate_count"]
    inlines = [ImageInline, ]


@admin.register(CouponImage)
class CouponImageAdmin(admin.ModelAdmin):
    list_display = ["id", "coupon"]
    search_fields = ["coupon__title"]
    autocomplete_fields = ["coupon"]


@admin.register(LineCoupon)
class LineCouponAdmin(admin.ModelAdmin):
    list_display = ["title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer","sell_count" ]
    list_editable = ["is_main", "price", "offer_percent", "count","sell_count"]
    list_filter = ["is_main", ]
    search_fields = ["title", "coupon__title"]
    autocomplete_fields = ["coupon", ]
    readonly_fields = ["price_with_offer", ]


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ["coupon", "user", "rate"]
    list_editable = ["rate", ]
    list_filter = ["rate", ]
    search_fields = ["coupon__title", "user__username"]
    autocomplete_fields = ["coupon", "user"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["coupon", "user", "parent", "created_at", "verified"]
    list_editable = ["verified", ]
    list_filter = ["created_at", "verified"]
    search_fields = ["coupon__title", "user__username", "text"]
    autocomplete_fields = ["coupon", "user", "parent"]
