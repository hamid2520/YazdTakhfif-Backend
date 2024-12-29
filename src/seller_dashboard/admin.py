from django.contrib import admin

from django_rest_passwordreset.models import ResetPasswordToken
from azbankgateways.models import Bank
from rest_framework.authtoken.models import TokenProxy
from social_django.models import Association, Nonce, UserSocialAuth
from django_summernote.models import Attachment
from django_celery_beat.models import SolarSchedule, IntervalSchedule, ClockedSchedule, CrontabSchedule, PeriodicTasks, \
    PeriodicTask
from django.contrib.auth.models import Group

admin.site.unregister(TokenProxy)
admin.site.unregister(Group)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
admin.site.unregister(ResetPasswordToken)
admin.site.unregister(Bank)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
# admin.site.unregister(PeriodicTasks)
admin.site.unregister(PeriodicTask)
admin.site.unregister(Attachment)
