from collections import (
    defaultdict,
)

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)

from factory_bo.consts import (
    GENERATED_ACTUAL_PREFIX,
    GENERATED_PREFIX,
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

        stage = 'web-bb-salary-etalon'
        project = 'web-bb-core'
        file_path = (
            f'{settings.FACTORY_BO__FIXTURES_DIR_PATH}/'
            f'{project.replace("-", "_")}_need_check_{{target}}_factories.csv'
        )
        with open(file_path.format(target='etalon'), 'a+') as etalon_file:
            etalon_file.write(f'{stage},\n')
            with open(file_path.format(target='generated_actual'), 'a+') as generated_actual_file:  # noqa
                generated_actual_file.write(f'{stage},\n')
                with open(file_path.format(target='generated'), 'a+') as generated_file:  # noqa
                    generated_file.write(f'{stage},\n')

                    for module_path, existing_factories in factory_classes.items():  # noqa
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
                            factory_class_name = (
                                existing_factory.factory_class_name
                            )

                            model.objects = model._base_manager

                            file = None

                            if (
                                model.objects.exists() and
                                factory_class_name.startswith(GENERATED_PREFIX)
                            ):
                                file = etalon_file
                            elif factory_class_name.startswith(GENERATED_ACTUAL_PREFIX):  # noqa
                                file = generated_actual_file
                            elif factory_class_name.startswith(GENERATED_PREFIX):  # noqa
                                file = generated_file

                            if file:
                                file.write(
                                    f'{module_path},{factory_class_name}\n'
                                )
