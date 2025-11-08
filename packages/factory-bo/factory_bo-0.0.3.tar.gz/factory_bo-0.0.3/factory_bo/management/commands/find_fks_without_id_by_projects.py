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
            f'{project.replace("-", "_")}_wrong_fk_ids.csv'
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
                    get_or_create_fields = (
                        existing_factory.factory_class.get_django_get_or_create()
                    )

                    model.objects = model._base_manager

                    wrong_fks = set()

                    for field in model._meta.fields:
                        if (
                            isinstance(field, ForeignKey) and
                            field.attname.replace('_id', '') in get_or_create_fields
                        ):
                            wrong_fks.add(field.attname)

                    if wrong_fks:
                        f.write(
                            f'{existing_factory.factory_class_name}, {";".join(wrong_fks)}\n'
                        )
