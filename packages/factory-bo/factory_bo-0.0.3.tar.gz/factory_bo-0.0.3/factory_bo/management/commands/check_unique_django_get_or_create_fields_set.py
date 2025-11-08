from django.conf import (
    settings,
)
from django.core.exceptions import (
    ValidationError,
)
from django.core.management import (
    BaseCommand,
)
from django.db.models import (
    Count,
)

from factory_bo.storages import (
    ExistingFactoryStorage,
)


class Command(BaseCommand):
    """
    Команда для проверки набора полей django_get_or_create на предмет
    уникальной выборки записей
    """

    def handle(self, *args, **options):
        existing_factory_storage = ExistingFactoryStorage()

        project = 'web-bb-core'
        file_path = (
            f'{settings.FACTORY_BO__FIXTURES_DIR_PATH}/'
            f'{project.replace("-", "_")}_need_check_generated_actual_factories.csv'  # noqa
        )
        with open(file_path, 'r') as generated_file:
            factory_class_names = list(
                filter(
                    lambda x: x and 'ForCopy' not in x,
                    [
                        item.split(',')[1].replace('\n', '').replace('Generated', '')  # noqa
                        for item in generated_file.readlines()
                    ]
                )
            )

            for factory_class_name in factory_class_names:
                existing_factory = existing_factory_storage.get_factory_class_by_name(  # noqa
                    factory_class_name=factory_class_name,
                )
                if not existing_factory:
                    raise ValidationError(
                        f'Factory class with name "{factory_class_name}" not '
                        f'found!'
                    )

                model = existing_factory.factory_class.get_model()

                model.objects = model._base_manager

                primary_key = model._meta.pk.column

                duplicate_records = model.objects.values(
                    *existing_factory.get_or_create_fields
                ).annotate(
                    duplicates_count=Count(primary_key),
                ).filter(
                    duplicates_count__gt=1,
                )

                if duplicate_records.exists():
                    print(
                        f'\n\nDuplicate records found! Factory class name - '
                        f'{factory_class_name}, django_get_or_create - '
                        f'({", ".join(existing_factory.get_or_create_fields)})'
                        f'\n\n{duplicate_records.query}'
                    )
