from ichec_django_core.serializers import (
    NestedHyperlinkedModelSerializer,
    PopulatedFormSerializer,
)

from ..models import Dataset


class DatasetSerializer(NestedHyperlinkedModelSerializer):

    form = PopulatedFormSerializer()

    class Meta:
        model = Dataset
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "creator",
            "title",
            "description",
            "uri",
            "is_public",
            "access_instructions",
            "equipment",
            "facility",
            "template",
            "form",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + ("creator",)

    def create(self, validated_data):

        form = validated_data.pop("form")
        if form:
            form_instance = PopulatedFormSerializer().create(form)
        else:
            form = None

        many_to_many = self.pop_many_to_many(validated_data)
        instance = Dataset.objects.create(form=form_instance, **validated_data)
        self.add_many_to_many(instance, many_to_many)
        return instance
