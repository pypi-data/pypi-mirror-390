from collections import (
    defaultdict,
)

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)
from django.db.models import (
    ForeignKey,
)

from factory_bo.storages import (
    ExistingFactoryStorage,
)


class Command(BaseCommand):
    """
    Команда для сбора оставшихся сгенерированных фабрик по проектам
    """

    def handle(self, *args, **options):
        existing_factory_storage = ExistingFactoryStorage()

        model_default_factory_map = (
            existing_factory_storage.get_model_default_factory_map()
        )

        factory_classes = defaultdict(set)

        for existing_factory in model_default_factory_map.values():
            factory_classes[existing_factory.module_path].add(existing_factory)

        project = 'web-bb-salary'
        file_path = (
            f'{settings.FACTORY_BO__FIXTURES_DIR_PATH}/'
            f'{project.replace("-", "_")}_self_fks.csv'
        )
        with open(file_path, 'a+') as f:
            for module_path, existing_factories in factory_classes.items():
                if project not in module_path:
                    continue

                sorted_existing_factories = (
                    sorted(
                        existing_factories,
                        key=lambda item: item.factory_class_name,
                    )
                )

                for existing_factory in sorted_existing_factories:
                    model = existing_factory.factory_class._meta.model

                    model.objects = model._base_manager

                    self_fks = set()

                    for field in model._meta.fields:
                        if (
                            isinstance(field, ForeignKey) and
                            field.related_model.__name__ == model.__name__
                        ):
                            self_fks.add(field.attname)

                    if self_fks:
                        f.write(
                            f'{module_path},{model.__name__}, {";".join(self_fks)}\n'
                        )
