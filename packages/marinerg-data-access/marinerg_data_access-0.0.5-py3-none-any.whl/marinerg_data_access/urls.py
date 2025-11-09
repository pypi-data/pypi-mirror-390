from .view_sets import DatasetViewSet, DatasetTemplateViewSet


def register_drf_views(router):
    router.register(r"datasets", DatasetViewSet)
    router.register(r"dataset_templates", DatasetTemplateViewSet)


urlpatterns: list = []
