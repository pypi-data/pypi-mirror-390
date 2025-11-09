from pydantic import BaseModel
from ichec_django_core.utils.test_utils.models import (
    Timestamped,
    FormCreate,
    FormDetail,
    FormFieldDetail,
    register_types,
    PopulatedFormCreate,
    PopulatedFormDetail,
)


class DatasetBase(BaseModel, frozen=True):

    title: str
    description: str = ""
    uri: str | None = None
    is_public: bool = True
    access_instructions: str | None = None
    equipment: str | None = None
    facility: str | None = None
    template: str | None = None


class DatasetCreate(DatasetBase, frozen=True):

    form: PopulatedFormCreate | None = None


class DatasetDetail(Timestamped, DatasetBase, frozen=True):

    form: PopulatedFormDetail | None = None
    creator: str


class DatasetList(DatasetDetail, frozen=True):
    pass


class DatasetTemplateBase(BaseModel, frozen=True):

    title: str
    description: str = ""
    uri: str | None = None
    is_public: bool = True
    access_instructions: str | None = None
    equipment: str | None = None
    facility: str | None = None
    template: str | None = None


class DatasetTemplateCreate(DatasetTemplateBase, frozen=True):

    form: FormCreate


class DatasetTemplateDetail(Timestamped, DatasetTemplateBase, frozen=True):

    form: FormDetail
    creator: str

    def get_field(self, key: str) -> FormFieldDetail | None:
        for group in self.form.groups:
            for field in group.fields:
                if field.key == key:
                    return field
        return None


class DatasetTemplateList(DatasetTemplateDetail, frozen=True):
    pass


register_types(
    "datasets",
    {"create": DatasetCreate, "detail": DatasetDetail, "list": DatasetList},
)

register_types(
    "dataset_templates",
    {"create": DatasetTemplateCreate, "detail": DatasetTemplateDetail},
)
