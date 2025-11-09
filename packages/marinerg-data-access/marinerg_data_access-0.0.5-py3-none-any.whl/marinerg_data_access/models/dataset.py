from django.db import models

from ichec_django_core.models import Member, PopulatedForm, TimesStampMixin

from marinerg_facility.models import Facility, Equipment

from .dataset_template import DatasetTemplate


class Dataset(TimesStampMixin):

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)

    title = models.CharField(max_length=250)

    description = models.TextField(blank=True)

    uri = models.CharField(max_length=250, null=True)

    is_public = models.BooleanField(default=True)

    access_instructions = models.TextField(blank=True, null=True)

    equipment = models.ForeignKey(
        Equipment, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    facility = models.ForeignKey(
        Facility, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    template = models.ForeignKey(
        DatasetTemplate, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    form = models.OneToOneField(PopulatedForm, null=True, on_delete=models.CASCADE)
