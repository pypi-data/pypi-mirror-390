import re
from collections import (
    defaultdict,
)
from typing import (
    List,
    Optional,
)

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)
from django.db.models import (
    Model,
)
from isort.api import (
    sort_code_string,
)

from factory_bo.consts import (
    ACTUAL_PREFIX,
    GENERATED_PREFIX,
    TAB_STR,
)
from factory_bo.factories import (
    ExistingFactory,
)
from factory_bo.storages import (
    ExistingFactoryStorage,
)
from factory_bo.strings import (
    FACTORY_CLASS_WITHOUT_COMMENT_STR,
    IMPORT_DEFAULT_MANAGER_FACTORY_STR,
    IMPORT_FACTORY_USE_TYPE_ENUM_STR,
)


class Command(BaseCommand):
    """
    Команда для негерации фабрик для моделей, у которых отсутствует дефолтная
    фабрика

    Для моделей, не относящихся к проектам, фабрики будут генерировать в
    директории

    FACTORY_BO__FIXTURES_DIR_PATH/features/factories/{app_label}.py
    """

    def _generate_factory_class_name(
        self,
        model: Model,
    ) -> str:
        """
        Генерация имени фабрики для модели
        """
        model_class_name = model._meta.label.split('.')[1]

        model_class_name_parts = list(
            map(
                lambda part: (
                    part.title() if
                    part.islower() else
                    part
                ),
                model_class_name.split('_')
            )
        )

        return f'GeneratedActual{"".join(model_class_name_parts)}Factory'

    def _write_imports(
        self,
        content: str,
    ) -> str:
        """
        Запись в файл импорта базового класа фабрик DefaultManagerFactory
        """
        imports = []

        if 'DefaultManagerFactory' in content:
            imports.append(IMPORT_DEFAULT_MANAGER_FACTORY_STR)

        return '\n'.join([content, *imports])

    def _sort_imports(
        self,
        content: str,
    ) -> str:
        """
        Сортировка импортов
        """
        return sort_code_string(
            code=content,
            config=settings.ISORT_CONFIG,
        )

    def _get_model_get_or_create_fields(
        self,
        model: Model,
        existing_factory: Optional[ExistingFactory] = None
    ) -> str:
        """
        Получение списка полей django_get_or_create в виде строки с
        перечислением через запятую
        """
        model_field_names = [
            field.name
            for field in model._meta.fields
        ]
        django_get_or_create_fields = set()

        if 'name' in model_field_names:
            django_get_or_create_fields.add('name')

        django_get_or_create_fields.update(
            set(model_field_names).intersection(
                settings.FACTORY_BO__PSEUDO_SELF_FK_IDS
            )
        )

        django_get_or_create_fields.update(
            set(model_field_names).intersection(
                settings.FACTORY_BO__PSEUDO_FK_IDS
            )
        )

        if existing_factory:
            field_names = (
                existing_factory.factory_class.get_django_get_or_create()
            )
            django_get_or_create_fields.update(
                [
                    field_name
                    for field_name in field_names if
                    '_id' not in field_name
                ]
            )

        django_get_or_create_fields_str = f'{TAB_STR*2}'
        if django_get_or_create_fields:
            django_get_or_create_fields_str = ',\n'.join(
                sorted(
                    map(
                        lambda field_str: f'{TAB_STR*3}\'{field_str}\'',  # noqa
                        django_get_or_create_fields
                    )
                )
            )
            django_get_or_create_fields_str = (
                f'{django_get_or_create_fields_str},'
            )

        return django_get_or_create_fields_str

    def _generate_actual_factory_for_model(
        self,
        content: str,
        existing_factories: List[ExistingFactory],
    ) -> str:
        generated_entities = []

        for existing_factory in existing_factories:
            model = existing_factory.factory_class._meta.model

            django_get_or_create_str = (
                self._get_model_get_or_create_fields(
                    model=model,
                    existing_factory=existing_factory,
                )
            )

            factory_class_name = self._generate_factory_class_name(
                model=model,
            )

            base_factory_class = 'DefaultManagerFactory'

            generated_entities.append(
                FACTORY_CLASS_WITHOUT_COMMENT_STR.format(
                    base_factory_class=base_factory_class,
                    factory_class_name=factory_class_name,
                    model_label=model._meta.label,
                    django_get_or_create_str=django_get_or_create_str,
                )
            )

        return ''.join([content, *generated_entities])

    def _mark_default_factories_as_custom(
        self,
        module_path: str,
        factory_class_names,
    ) -> str:
        """
        В файлах фабрик производится пометка дефолтной фабрики, как кастомной
        для дальнейшей генерации актуальной, на ее основе
        """
        code_lines = []
        with open(module_path) as original_file:
            need_add_blank_line = False
            for line in original_file:
                if any(map(lambda name: f'class {name}(' in line, factory_class_names)):
                    line = re.sub(
                        r'(class [\w\d_]+Factory\([\w\d_]+\):)',
                        r'\g<1>\n    _factory_use_type = FactoryUseTypeEnum.CUSTOM',  # noqa
                        line
                    )

                    need_add_blank_line = True
                else:
                    if need_add_blank_line and line and line != '\n':
                        line = f'\n{line}'

                    need_add_blank_line = False

                code_lines.append(line)

        code_lines.append(IMPORT_FACTORY_USE_TYPE_ENUM_STR)

        code = ''.join(code_lines)

        return code

    def handle(self, *args, **options):
        existing_factory_storage = ExistingFactoryStorage()

        model_default_factory_map = (
            existing_factory_storage.get_model_default_factory_map()
        )

        factory_classes = defaultdict(set)

        for existing_factory in model_default_factory_map.values():
            if (
                existing_factory.factory_class_name.startswith(GENERATED_PREFIX) or  # noqa
                existing_factory.factory_class_name.startswith(ACTUAL_PREFIX)
            ):
                continue

            factory_classes[existing_factory.module_path].add(existing_factory)

        for module_path, existing_factories in factory_classes.items():
            if 'web-bb-salary' not in module_path:
                continue

            factory_class_names = list(
                existing_factory.factory_class_name
                for existing_factory in existing_factories
            )
            code = self._mark_default_factories_as_custom(
                module_path=module_path,
                factory_class_names=factory_class_names,
            )

            code = self._generate_actual_factory_for_model(
                content=code,
                existing_factories=existing_factories,
            )

            code = self._write_imports(
                content=code,
            )

            code = self._sort_imports(
                content=code,
            )

            with open(module_path, 'w') as original_file:
                original_file.write(code)
