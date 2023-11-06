from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import LineCoupon
from src.basket.models import ProductValidationCode
from .exceptions import MaximumNumberOfDeletableObjectsError


@receiver(post_save, sender=LineCoupon)
def line_coupon_codes_generator(sender, **kwargs):
    line_coupon: LineCoupon = kwargs["instance"]
    # product_codes = ProductValidationCode.objects.filter(product_id=line_coupon.id)
    product_codes = line_coupon.productvalidationcode_set.all()
    diff_count = line_coupon.count - product_codes.count()
    if diff_count > 0:
        ProductValidationCode.objects.bulk_create(
            (ProductValidationCode(product_id=line_coupon.id) for _ in range(diff_count)))
        pass
    elif diff_count < 0:
        diff_count = abs(diff_count)
        delete_codes_pk_list = product_codes.filter(used=False).order_by("-id")[:diff_count].values_list("id")
        if delete_codes_pk_list.count() < diff_count:
            raise MaximumNumberOfDeletableObjectsError()
        delete_codes = ProductValidationCode.objects.filter(pk__in=delete_codes_pk_list).delete()
