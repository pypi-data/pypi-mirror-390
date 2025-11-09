from django.db import models

from ichec_django_core.models import Member, Form, TimesStampMixin


class DatasetTemplate(TimesStampMixin):

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)

    title = models.CharField(max_length=250)

    description = models.TextField(blank=True)

    form = models.OneToOneField(Form, on_delete=models.CASCADE)
