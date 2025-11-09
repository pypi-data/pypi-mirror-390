from ichec_django_core.utils.test_utils.models import (
    FormCreate,
    FormGroupCreate,
    FormFieldCreate,
    PopulatedFormCreate,
    FormFieldValueCreate,
)

from .models import (
    DatasetCreate,
    DatasetTemplateDetail,
    DatasetTemplateCreate,
)


def create_dataset_templates(
    count: int = 10,
    offset: int = 0,
) -> list[DatasetTemplateCreate]:

    contents = []
    for idx in range(offset, count + offset):
        fields = [
            FormFieldCreate(
                label="Measurement Unit",
                key="measurement_unit",
                field_type="TEXT",
                required=True,
                default="",
                description="Enter the base measurement unit used.",
            ),
            FormFieldCreate(
                label="Notes",
                key="notes",
                field_type="TEXT",
                required=False,
                default="",
                description="Add supporting test notes.",
            ),
        ]

        groups = [FormGroupCreate(fields=fields)]

        contents.append(
            DatasetTemplateCreate(
                title=f"Dataset Template {idx}",
                description=f"Description of dataset template {idx}",
                form=FormCreate(groups=groups),
            )
        )
    return contents


def create_datasets(template: DatasetTemplateDetail, count: int = 10, offset: int = 0):

    unit_field = template.get_field("measurement_unit")
    if not unit_field:
        raise RuntimeError("Field not found")

    contents = []
    for idx in range(offset, count + offset):
        contents.append(
            DatasetCreate(
                title=f"Scripted dataset {idx}",
                description=f"Description of scripted dataset {idx}",
                uri=f"http://www.dataset_{idx}.org",
                form=PopulatedFormCreate(
                    values=[
                        FormFieldValueCreate(
                            field=unit_field.id, value="measurement_unit"
                        )
                    ]
                ),
            )
        )
    return contents
