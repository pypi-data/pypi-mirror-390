from ichec_django_core.serializers import (
    NestedHyperlinkedModelSerializer,
    FormSerializer,
)

from ..models import DatasetTemplate


class DatasetTemplateSerializer(NestedHyperlinkedModelSerializer):

    form = FormSerializer()

    class Meta:
        model = DatasetTemplate
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "creator",
            "title",
            "description",
            "form",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + ("creator",)

    def create(self, validated_data):

        form = validated_data.pop("form")
        form_instance = FormSerializer().create(form)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = DatasetTemplate.objects.create(form=form_instance, **validated_data)
        self.add_many_to_many(instance, many_to_many)
        return instance
