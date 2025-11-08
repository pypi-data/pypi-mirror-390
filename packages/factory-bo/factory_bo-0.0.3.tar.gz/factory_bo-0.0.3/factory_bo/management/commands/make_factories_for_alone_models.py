import os
from collections import (
    defaultdict,
)
from typing import (
    Dict,
    List,
    Set,
    Tuple,
)

from django.apps import (
    AppConfig,
    apps,
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
    TAB_STR,
)
from factory_bo.storages import (
    ExistingFactoryStorage,
)
from factory_bo.strings import (
    FACTORY_CLASS_STR,
    IMPORT_DEFAULT_MANAGER_FACTORY_STR,
)


class Command(BaseCommand):
    """
    Команда для генерации фабрик для моделей, у которых отсутствует дефолтная
    фабрика

    Для моделей, не относящихся к проектам, фабрики будут генерироваться в
    директории

    FACTORY_BO__FIXTURES_DIR_PATH/features/factories/{app_label}.py
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps_list',
            action='store',
            dest='apps_list',
            help=(
                'List of apps to generate factories.'
            )
        )
        parser.add_argument(
            '--exclude_apps',
            action='store',
            dest='exclude_apps',
            help=(
                'Exclude apps'
            )
        )

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

        return f'Generated{"".join(model_class_name_parts)}Factory'

    def _write_import_web_bb_model_factory(
        self,
        content: str,
        generated_entities: List[str]
    ):
        """
        Запись в файл импортов базовых классов фабрик
        """
        imports_map = {
            'DefaultManagerFactory': IMPORT_DEFAULT_MANAGER_FACTORY_STR,
        }

        for class_name, import_path in imports_map.items():
            if (
                class_name not in content and
                any(class_name in entity for entity in generated_entities)
            ):
                generated_entities.insert(0, import_path)

    def _check_or_create_factories_module(
        self,
        app_label: str,
        app_path: str,
    ) -> Tuple[str, str]:
        """
        Метод создания модуля для фабрик.

        Если модуль создан, то ничего делать не надо.
        """
        # Если модель не из проекта, то выгрузим фабрики отдельно для
        # дальнейшего распределения руками
        if 'web-bb-' not in app_path and 'web_bb_' not in app_path:
            app_path = settings.FACTORY_BO__FIXTURES_DIR_PATH

        features_path = os.path.join(app_path, 'features')
        factories_path = os.path.join(features_path, 'factories')

        os.makedirs(
            name=factories_path,
            exist_ok=True,
        )

        for path in (features_path, factories_path):
            init_py_path = os.path.join(path, '__init__.py')
            if not os.path.exists(init_py_path):
                os.mknod(
                    path=init_py_path,
                    mode=0o777,
                )

        factory_module_path = os.path.join(factories_path, f'{app_label}.py')
        if os.path.exists(factory_module_path):
            with open(factory_module_path) as f:
                content = f.read()
        else:
            content = ''

        return factory_module_path, content

    def _sort_imports(
        self,
        content: str,
    ):
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

        django_get_or_create_fields_str = f'{TAB_STR*2}#'
        if django_get_or_create_fields:
            django_get_or_create_fields_str = ',\n'.join(
                sorted(
                    map(
                        lambda field_str: f'{TAB_STR*2}# {TAB_STR}\'{field_str}\'',  # noqa
                        django_get_or_create_fields
                    )
                )
            )
            django_get_or_create_fields_str = (
                f'{django_get_or_create_fields_str},'
            )

        return django_get_or_create_fields_str

    def _generate_factory_for_model(
        self,
        grouped_models_by_apps: Dict[Tuple[str, str], Set[Model]],
    ):
        for (app_label, app_path), models in grouped_models_by_apps.items():
            factory_module_path, content = (
                self._check_or_create_factories_module(
                    app_label=app_label,
                    app_path=app_path,
                )
            )

            generated_entities = []

            self._write_import_web_bb_model_factory(
                content=content,
                generated_entities=generated_entities,
            )
            for model in models:
                django_get_or_create_str = (
                    self._get_model_get_or_create_fields(
                        model=model,
                    )
                )

                factory_class_name = self._generate_factory_class_name(
                    model=model,
                )

                base_factory_class = 'DefaultManagerFactory'

                generated_entities.append(
                    FACTORY_CLASS_STR.format(
                        base_factory_class=base_factory_class,
                        factory_class_name=factory_class_name,
                        model_label=model._meta.label,
                        django_get_or_create_str=django_get_or_create_str,
                    )
                )

            self._write_import_web_bb_model_factory(
                content=content,
                generated_entities=generated_entities,
            )

            content = ''.join([content, *generated_entities])

            content = self._sort_imports(
                content=content,
            )

            with open(factory_module_path, 'w') as f:
                f.write(content)

    def _get_apps_configs(self, options: Dict) -> List[AppConfig]:
        """Получение списка AppConfig приложений в соответствии с переданными аргументами.

        Args:
            options: Словарь аргументов командной строки.

        Returns:
            Список AppConfig.

        Raises:
            ValueError: Если передано неверное название приложения.
        """
        apps_configs = []

        if options['apps_list']:
            apps_list = list(filter(None, options.get('apps_list', '').split(',')))
            for app_name in apps_list:
                try:
                    app_config = apps.app_configs[app_name]
                except KeyError as e:
                    raise ValueError(f'No app found with name "{app_name}"') from e
                else:
                    apps_configs.append(app_config)
        else:
            exclude_apps = list(filter(None, options.get('exclude_apps', '').split(',')))
            exclude_apps.extend(settings.FACTORY_BO__EXCLUDED_APPS)
            for app_name, app_config in apps.app_configs.items():
                if app_name in exclude_apps:
                    continue
                apps_configs.append(app_config)

        return apps_configs

    def handle(self, *args, **options):
        apps_configs = self._get_apps_configs(options)

        models = []
        for app_config in apps_configs:
            models.extend(app_config.get_models(include_auto_created=True))

        existing_factory_storage = ExistingFactoryStorage(
            raise_on_nonexistent=False,
        )

        grouped_models_by_apps = defaultdict(set)

        for model in models:
            model_label = model._meta.label
            app_label = model._meta.app_label
            app_path = model._meta.app_config.path

            if (
                model_label in settings.FACTORY_BO__EXCLUDED_MODELS or
                existing_factory_storage.model_factories_map.get(model_label, {}) or
                model._meta.proxy
            ):
                continue

            grouped_models_by_apps[(app_label, app_path)].add(model)

        self._generate_factory_for_model(
            grouped_models_by_apps=grouped_models_by_apps,
        )
