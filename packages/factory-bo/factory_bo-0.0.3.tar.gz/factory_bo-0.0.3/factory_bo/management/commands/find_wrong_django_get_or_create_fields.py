import os

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)

from factory_bo.storages import (
    ExistingFactoryStorage,
)


class Command(BaseCommand):
    """
    Команда для поиска использования запрещенных полей наборе
    django_get_or_create
    """
    def handle(self, *args, **options):
        existing_factory_storage = ExistingFactoryStorage()

        default_model_factories_map = (
            existing_factory_storage.get_model_default_factory_map()
        )

        with open(os.path.join(settings.FACTORY_BO__FIXTURES_DIR_PATH, 'wrong_factory_fields.csv'), 'w') as f:  # noqa
            for model_label, existing_factory in default_model_factories_map.values():  # noqa
                get_or_create_fields = set(
                    existing_factory.factory_class.get_django_get_or_create()
                )

                model_fields = (
                    existing_factory_storage.model_storage.get_allowed_fields(
                        model_label=model_label,
                    )
                )

                for field in get_or_create_fields:
                    if (
                        field not in model_fields
                    ):
                        f.write(
                            f'{existing_factory.factory_class_name},{field}\n'  # noqa
                        )
