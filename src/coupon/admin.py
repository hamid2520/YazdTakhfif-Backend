from django.forms import Form
from django.contrib import admin

from src.coupon.models import Category, Coupon, LineCoupon


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent", "level"]
    list_filter = ["parent", "level"]
    list_editable = ["parent", "level"]


class CouponAdmin(admin.ModelAdmin):
    list_display = ["title", "business", "created", "expire_date"]
    list_filter = ["business", "category", "created", "expire_date"]


class LineCouponAdmin(admin.ModelAdmin):
    list_display = ["title", "coupon", "is_main", "discount_percent", "price", "final_price"]
    list_filter = ["coupon", "is_main"]
    list_editable = ["discount_percent", "price"]
    readonly_fields = ["final_price", ]

    def save_model(self, request, obj, form: Form, change):
        queryset = LineCoupon.objects.filter(coupon=form.cleaned_data.get("coupon"), is_main=True)
        if queryset.exists():
            raise ValueError("Only one Line coupon can be active!")
        return super().save_model(request, obj, form, change)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(LineCoupon, LineCouponAdmin)
