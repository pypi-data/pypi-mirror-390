import inspect
import json
import sys
import uuid
import warnings
from abc import (
    ABCMeta,
    abstractmethod,
)
from copy import (
    copy,
)
from importlib import (
    import_module,
)
from importlib.util import (
    module_from_spec,
    spec_from_file_location,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.core.exceptions import (
    ValidationError,
)
from django.db.models import (
    Field,
    FileField,
    ForeignKey,
    Model,
    UUIDField,
)

from factory_bo.base import (
    DefaultManagerFactory,
)
from factory_bo.consts import (
    CONTENT_TYPE_MODEL,
    EXCLUDED_FIELD_CLASSES,
    FACTORY_CLASS_NAME_DELIMETER,
    GENERATED_PREFIX,
)
from factory_bo.enums import (
    FactoryUseTypeEnum,
    PreparingModelRecordTagEnum,
)
from factory_bo.factories import (
    ExistingFactory,
)
from factory_bo.helpers import (
    colored_stdout_output,
    substitute_model_get_queryset_method,
)
from factory_bo.records import (
    ModelRecord,
    PreparingModelRecord,
)
from factory_bo.signals import (
    existing_factory_prepare_filter,
)
from factory_bo.strings import (
    DISALLOWED_DJANGO_GET_OR_CREATE_FIELDS_FOUND_ERROR,
    FACTORIES_FOR_MODEL_NOT_FOUND,
    FACTORY_CLASS_FOR_MODEL_NOT_FOUND,
    MODEL_WITHOUT_DEFAULT_FACTORY_ERROR,
    RECORD_FOR_FK_FIELD_NOT_FOUND_ERROR,
    SEVERAL_MODEL_DAFAULT_FACTORIES_ERROR,
    USING_GENERATED_FACTORY_WARNING,
    WRONG_FACTORY_USE_TYPE_ERROR,
)


class ModelStorage:
    """
    Хранилище доступных моделей согласно подключенных плагинов, исключенных
    моделей и приложений

    Лучше использовать в связке с ExistingFactoryStorage, т.к. производится
    дополнительная проверка корректности фабрик
    """
    def __init__(self):
        self._models: Dict[str, Dict[str, Union[Type[Model], Dict[str, Field], Dict[str, str]]]] = {}  # noqa

        self._prepare()

    def _prepare_allowed_fields(
        self,
        model: Type[Model],
    ):
        """
        Добавление допустимых полей модели
        """
        allowed_fields = self._models[model._meta.label]['allowed_fields']

        for field in model._meta.fields:
            if (
                getattr(field, 'auto_now', False) or
                getattr(field, 'auto_now_add', False) or
                isinstance(field, FileField)
            ):
                continue

            allowed_fields[field.attname] = field

    def _prepare_foreign_key_fields_map(
        self,
        model: Type[Model],
    ):
        """
        Добавление полей внешних ключей с указанием моделей, на которые
        производится ссылка
        """
        foreign_key_fields_map = (
            self._models[model._meta.label]['foreign_key_fields_map']
        )
        processed_field_names = set()

        allowed_fields = self._models[model._meta.label]['allowed_fields']

        # Заполнение явных внешних ключей и
        # обработка ForeignKey
        fk_field_model_label_map = {
            field.attname: field.related_model._meta.label
            for field in allowed_fields.values() if (
                isinstance(field, ForeignKey) and
                field.attname not in processed_field_names
            )
        }

        foreign_key_fields_map.update(**fk_field_model_label_map)

        processed_field_names.update(fk_field_model_label_map.keys())

        # Заполнение псевдо внешних ключей указывающих на другие модели
        pseudo_fk_field_names = (
            set(settings.FACTORY_BO__PSEUDO_FK_IDS).intersection(
                allowed_fields.keys()
            ).difference(processed_field_names)
        )

        pseudo_fk_field_model_label_map = {
            field_name: settings.FACTORY_BO__PSEUDO_FK_IDS[field_name]
            for field_name in pseudo_fk_field_names
        }

        foreign_key_fields_map.update(**pseudo_fk_field_model_label_map)

        processed_field_names.update(pseudo_fk_field_names)

        # Заполнение псевдо внешних ключей, указывающих на ту же модель
        self_fk_field_names = (
            set(settings.FACTORY_BO__PSEUDO_SELF_FK_IDS).intersection(
                allowed_fields.keys()
            ).difference(processed_field_names)
        )

        self_fk_field_model_label_map = {
            field_name: model._meta.label
            for field_name in self_fk_field_names
        }

        foreign_key_fields_map.update(**self_fk_field_model_label_map)

    def _prepare(self):
        """
        Подготовка кеша моделей
        """
        allowed_models = filter(
            lambda model: not (
                model._meta.app_label in settings.FACTORY_BO__EXCLUDED_APPS or
                model._meta.label in settings.FACTORY_BO__EXCLUDED_MODELS or
                model._meta.proxy
            ),
            apps.get_models(include_auto_created=True)
        )

        for model in allowed_models:
            self._models[model._meta.label] = {
                'class_': model,
                'allowed_fields': {},
                'foreign_key_fields_map': {},
            }

            self._prepare_allowed_fields(
                model=model,
            )

            self._prepare_foreign_key_fields_map(
                model=model,
            )

    def get_model(
        self,
        model_label: str,
    ) -> Dict[str, Union[Type[Model], Dict[str, Field], Dict[str, str]]]:
        """
        Возвращает собранные данные модели
        """
        return self._models[model_label]

    def get_model_class(
        self,
        model_label: str,
    ) -> Optional[Type[Model]]:
        """
        Возращает класс модели из кеша по лейблу
        """
        model = None

        if model_label in self._models:
            model = self._models[model_label]['class_']

        return model

    def get_model_classes(self) -> List[Type[Model]]:
        """
        Возвращает все модели находящиеся в хранилище
        """
        return [
            model['class_']
            for model in self._models.values()
        ]

    def get_model_labels(self) -> List[str]:
        """
        Получение списка лейблов моделей, находящихся в хранилище
        """
        return [
            model['class_']._meta.label
            for model in self._models.values()
        ]

    def get_allowed_fields(
        self,
        model_label: str,
    ) -> Optional[List[Field]]:
        """
        Возращает допустимые поля модели
        """
        allowed_fields = None

        if model_label in self._models:
            allowed_fields = (
                self._models[model_label]['allowed_fields'].values()
            )

        return allowed_fields

    def get_allowed_field_names(
        self,
        model_label: str,
    ) -> Optional[List[str]]:
        """
        Возвращает имена допустимых полей
        """
        allowed_field_names = None

        if model_label in self._models:
            allowed_field_names = (
                self._models[model_label]['allowed_fields'].keys()
            )

        return allowed_field_names

    def get_model_foreign_key_fields_map(
        self,
        model_label: str,
    ):
        """
        Получение карты соответствия внешних ключей и лейблов моделей, на
        которые совершается ссылка
        """
        return self._models[model_label]['foreign_key_fields_map']

    def exists(
        self,
        model_label: str,
    ) -> bool:
        """
        Проверяет существование модели в хранилище
        """
        return model_label in self._models


class ExistingFactoryStorage:
    """
    Кеш существующих фабрик в проекте

    Кеш представляет из себя словарь, ключом которого является название фабрики,
    значением - именованный кортеж ExistingFactory с классом фабрики (
    factory_class) и путем модуля для импорта (import_path)
    """

    def __init__(
        self,
        model_storage: Optional[ModelStorage] = None,
        raise_on_nonexistent: Optional[bool] = True,
    ):
        if not model_storage:
            model_storage = ModelStorage()

        self._model_storage = model_storage
        self._model_factories_map: Dict[str, Dict[str, Union[ExistingFactory, Dict[str, ExistingFactory]]]] = {}  # noqa
        self._raise_on_nonexistent = raise_on_nonexistent

        self._prepare()

    @property
    def model_factories_map(self) -> Dict[str, Dict[str, Union[ExistingFactory, Dict[str, ExistingFactory]]]]:  # noqa
        return self._model_factories_map

    @property
    def model_storage(self) -> ModelStorage:
        return self._model_storage

    def get_model_factories_map(
        self,
        model_label: str,
    ) -> Dict[str, Union[ExistingFactory, Dict[str, ExistingFactory]]]:
        """
        Получение карты фабрик для модели
        """
        factories_map = self._model_factories_map.get(model_label)

        if not factories_map:
            raise ValueError(
                FACTORIES_FOR_MODEL_NOT_FOUND.format(
                    model_label=model_label,
                )
            )

        return factories_map

    def get_model_factories(
        self,
        model_label: str,
    ) -> Dict[str, ExistingFactory]:
        """
        Получение фабрик модели
        """
        factories_map = self.get_model_factories_map(
            model_label=model_label,
        )
        model_factories = {}

        model_factories.update(
            factories_map[FactoryUseTypeEnum.CUSTOM]
        )

        default_factory = factories_map[FactoryUseTypeEnum.DEFAULT]

        model_factories[default_factory.factory_class_name] = default_factory

        return model_factories

    def get_factory_class_for_model(
        self,
        model_label: str,
        factory_class_name: str,
    ) -> ExistingFactory:
        """
        Получение класса фабрики для модели
        """
        model_factories = self.get_model_factories(
            model_label=model_label,
        )

        if factory_class_name not in model_factories:
            raise ValueError(
                FACTORY_CLASS_FOR_MODEL_NOT_FOUND.format(
                    factory_class_name=factory_class_name,
                    model_label=model_label,
                )
            )

        if factory_class_name.startswith(GENERATED_PREFIX):
            colored_stdout_output(
                message=USING_GENERATED_FACTORY_WARNING.format(
                    generated_factory=factory_class_name,
                ),
                color=31,
            )

        return model_factories[factory_class_name]

    def get_model_default_factory(
        self,
        model_label: str,
    ) -> ExistingFactory:
        """
        Получение дефолтной фабрики модели
        """
        factories_map = self.get_model_factories_map(
            model_label=model_label,
        )

        return factories_map[FactoryUseTypeEnum.DEFAULT]

    def get_model_default_factory_map(self) -> Dict[str, ExistingFactory]:
        """
        Получение карты соответствия моделей и их дефолтных фабрик
        """
        model_default_factory_map = {}

        for model_label, factories_map in self._model_factories_map.items():
            default_factory = factories_map[FactoryUseTypeEnum.DEFAULT]

            model_default_factory_map[model_label] = default_factory

            if default_factory.factory_class_name.startswith(GENERATED_PREFIX):
                colored_stdout_output(
                    message=USING_GENERATED_FACTORY_WARNING.format(
                        generated_factory=default_factory.factory_class_name,
                    ),
                    color=31,
                )

        return model_default_factory_map

    def get_factories(self) -> List[ExistingFactory]:
        """
        Возвращает все фабрики хранилища
        """
        factories = []
        for factories_map in self._model_factories_map.values():
            factories.append(factories_map[FactoryUseTypeEnum.DEFAULT])

            factories.extend(factories_map[FactoryUseTypeEnum.CUSTOM].values())

        return factories

    def get_factory_class_by_name(
        self,
        factory_class_name: str,
    ) -> Optional[ExistingFactory]:
        """
        Метод получения класса фабрики по имени
        """
        existing_factory = None

        filtered_existing_factories = list(
            filter(
                lambda existing_factory: (
                    existing_factory and
                    existing_factory.factory_class_name == factory_class_name
                ),
                self.get_factories()
            )
        )

        if filtered_existing_factories:
            existing_factory = filtered_existing_factories[0]

        return existing_factory

    def _find_factories_modules(self) -> List[Tuple[str, str]]:
        """
        Поиск модулей содержащих фабрики
        """
        factories_modules = []

        checked_packed_paths = []
        for app_name in settings.INSTALLED_APPS:
            app_module = import_module(app_name)
            app_path = app_module.__path__

            # Если поиск уже осуществлялся по родительской директории,
            # то проверку нужно пропустить
            is_already_checked = False
            for cpp in checked_packed_paths:
                if app_path in cpp:
                    is_already_checked = True
                    break

            if is_already_checked:
                continue

            application_path = Path(app_path[0])
            factory_file_patterns = [
                '**/factories/**/*.py',
            ]

            for factory_file_pattern in factory_file_patterns:
                factory_modules_paths = application_path.glob(
                    factory_file_pattern
                )
                for factory_module_path in factory_modules_paths:
                    factory_module_path = str(factory_module_path)

                    # Нас не интересуют __init__.py
                    if '__init__.py' in factory_module_path:
                        continue

                    # Дополнительная фильтрация
                    filter_results = existing_factory_prepare_filter.send(
                        sender=app_name,
                        factory_module_path=factory_module_path,
                    )
                    filtered = False
                    for _, response in filter_results:
                        if not response:
                            filtered = True
                            break

                    if filtered:
                        continue

                    module_name = (
                        str(factory_module_path).split('/')[-1].split('.')[0]
                    )

                    spec = spec_from_file_location(
                        name=module_name,
                        location=factory_module_path,
                    )
                    factory_module = module_from_spec(
                        spec=spec,
                    )
                    spec.loader.exec_module(factory_module)
                    factories_modules.append(
                        (
                            factory_module,
                            factory_module_path,
                        )
                    )

                checked_packed_paths.append(app_path)

        return factories_modules

    def _get_module_import_path(self, module, sys_path) -> str:
        """
        Предназначен для получения пути пакета для импорта фабрики
        """
        module_path = module.__file__

        package_path = max(
            filter(
                lambda path: path in module_path,
                sys_path
            )
        )

        relative_module_path = module_path.split(f'{package_path}/')[1]
        import_path = '.'.join(relative_module_path.split('.')[0].split('/'))

        return import_path

    def _check_factory_class(
        self,
        factory_class: DefaultManagerFactory,
    ):
        """
        Проверка фабрики на допустимость к использованию и корректность
        """
        model_label = factory_class.get_model_label()

        is_allowed_factory = False

        if self._model_storage.exists(model_label):
            is_allowed_factory = True

        # TODO BOBUH-15824 После полного перехода на новые фабрики, в условии
        #  необходимо убрать проверку на тип использования - кастомный.
        #  Проверку должны проходить все фабрики без исключения
        if (
            is_allowed_factory and
            FactoryUseTypeEnum.is_default(factory_class.get_factory_use_type())
        ):
            wrong_fields = set(
                factory_class.get_django_get_or_create()
            ).difference(
                self._model_storage.get_allowed_field_names(model_label)
            )

            if wrong_fields:
                raise ValidationError(
                    DISALLOWED_DJANGO_GET_OR_CREATE_FIELDS_FOUND_ERROR.format(
                        disallowed_fields=', '.join(wrong_fields),
                        factory_class=factory_class.__name__,
                    )
                )

            wrong_excluded_fields = set(
                factory_class.get_django_get_or_create()
            ).intersection(
                factory_class.get_excluded_fk_fields()
            )

            if wrong_excluded_fields:
                raise ValidationError(
                    DISALLOWED_DJANGO_GET_OR_CREATE_FIELDS_FOUND_ERROR.format(
                        disallowed_fields=', '.join(wrong_excluded_fields),
                        factory_class=factory_class.__name__,
                    )
                )

            factory_use_type = factory_class.get_factory_use_type()

            if not FactoryUseTypeEnum.exists(factory_use_type):
                raise ValidationError(
                    WRONG_FACTORY_USE_TYPE_ERROR.format(
                        factory_use_type=factory_use_type,
                        factory_class_name=factory_class.__name__,
                    )
                )

            model_factories = (
                self._model_factories_map[model_label] if
                model_label in self._model_factories_map else
                None
            )

            if (
                model_factories and
                FactoryUseTypeEnum.is_default(factory_use_type) and
                model_factories[FactoryUseTypeEnum.DEFAULT] and
                factory_class.__name__ != model_factories[FactoryUseTypeEnum.DEFAULT].factory_class.__name__  # noqa
            ):
                second_factory_class_name = (
                    model_factories[FactoryUseTypeEnum.DEFAULT].factory_class.__name__# noqa
                )

                raise ValidationError(
                    SEVERAL_MODEL_DAFAULT_FACTORIES_ERROR.format(
                        model_label=model_label,
                        factories=(
                            f'{factory_class.__name__}, '
                            f'{second_factory_class_name}'
                        ),
                    )
                )

        return is_allowed_factory

    def _check_default_factory_model_exists(self):
        """
        Проверка существования дефолных фабрик для всех допустимых моделей.
        Если для модели нет дефолтной фабрики - нужно падать с ошибкой
        """
        model_default_factory_map = self.get_model_default_factory_map()

        models_without_default_factory = set()

        for model_label in self._model_storage.get_model_labels():
            if model_label not in model_default_factory_map:
                models_without_default_factory.add(model_label)

        if models_without_default_factory:
            error_message = MODEL_WITHOUT_DEFAULT_FACTORY_ERROR.format(
                model_labels=', '.join(sorted(models_without_default_factory)),
            )

            if self._raise_on_nonexistent:
                raise ValueError(error_message)
            else:
                warnings.warn(error_message)

    def _get_factory_class_name_alias(
        self,
        factory_class: DefaultManagerFactory,
    ) -> Optional[str]:
        """
        Возвращает сгенерированный алиас имени фабрики, если существует
        фабрика с таким же именем
        """
        factory_class_name_alias = None
        existing_factory_class = self.get_factory_class_by_name(
            factory_class_name=factory_class.__name__,
        )

        if (
            existing_factory_class and
            existing_factory_class.factory_model_label != factory_class.get_model_label()  # noqa
        ):
            uuid_hex_part = uuid.uuid4().hex[:6]

            factory_class_name_alias = (
                f'{factory_class.__name__}{FACTORY_CLASS_NAME_DELIMETER}'
                f'{uuid_hex_part}'
            )

        return factory_class_name_alias

    def _prepare(self):
        """
        Поиск фабрик во всех подключенных приложениях
        """
        sys_path = set(sys.path)

        factories_modules = self._find_factories_modules()
        for factory_module, module_path in factories_modules:
            factory_classes_names = list(filter(
                lambda name: (
                    inspect.isclass(getattr(factory_module, name)) and
                    issubclass(getattr(factory_module, name), DefaultManagerFactory) and  # noqa
                    not getattr(factory_module, name)._meta.abstract
                ),
                dir(factory_module)
            ))

            if factory_classes_names:
                import_path = self._get_module_import_path(
                    module=factory_module,
                    sys_path=sys_path,
                )

                for factory_class_name in factory_classes_names:
                    factory_class: DefaultManagerFactory = getattr(
                        factory_module,
                        factory_class_name
                    )

                    model_label = factory_class.get_model_label()

                    if not self._check_factory_class(factory_class):
                        continue

                    factory_class_name_alias = (
                        self._get_factory_class_name_alias(
                            factory_class=factory_class,
                        )
                    )

                    if model_label not in self._model_factories_map:
                        self._model_factories_map[model_label] = {
                            FactoryUseTypeEnum.DEFAULT: None,
                            FactoryUseTypeEnum.CUSTOM: {},
                        }

                    model_factories = self._model_factories_map[model_label]
                    factory_use_type = factory_class.get_factory_use_type()

                    existing_factory = ExistingFactory(
                        factory_class=factory_class,
                        factory_class_name_alias=factory_class_name_alias,
                        import_path=import_path,
                        module_path=module_path,
                    )

                    if FactoryUseTypeEnum.is_default(factory_use_type):
                        model_factories[FactoryUseTypeEnum.DEFAULT] = (
                            existing_factory
                        )
                    elif FactoryUseTypeEnum.is_custom(factory_use_type):
                        model_factories[FactoryUseTypeEnum.CUSTOM][factory_class_name] = (  # noqa
                            existing_factory
                        )

        self._check_default_factory_model_exists()


class PreparingModelRecordStorage:
    """
    Хранилище обрабатываемых записей моделей
    """

    def __init__(
        self,
        model_factory_correlation_storage: 'ModelFactoryCorrelationStorage',
        existing_factory_storage: ExistingFactoryStorage,
    ):
        self._records: Dict[Tuple[str, str], PreparingModelRecord] = {}

        self._model_factory_correlation_storage = (
            model_factory_correlation_storage
        )

        self._existing_factory_storage: ExistingFactoryStorage = (
            existing_factory_storage
        )

    @property
    def records(self) -> Dict[Tuple[str, str], PreparingModelRecord]:
        return self._records

    def _fill_fk_fields(
        self,
        model_record: ModelRecord,
        fk_source_storage: 'PreparingModelRecordStorage',
        fk_field_model_label_map: Dict[str, str],
    ):
        """
        Заполнение полей внешних ключей
        """
        for field_name, model_label in fk_field_model_label_map.items():
            record_field = model_record.fields.get(field_name)

            if record_field:
                if not isinstance(
                    record_field,
                    PreparingModelRecord,
                ):
                    field_value_id = model_record.fields.pop(field_name)

                    if field_value_id == 'None':
                        field_value = 'None'
                    else:
                        key = (
                            model_label,
                            field_value_id,
                        )

                        try:
                            field_value = (
                                fk_source_storage.records.get(key) or
                                self._records[key]
                            )
                        except KeyError:
                            raise KeyError(
                                RECORD_FOR_FK_FIELD_NOT_FOUND_ERROR.format(
                                    model_label=model_record.model_label,
                                    field_name=field_name,
                                    related_record=model_label,
                                    field_value_id=field_value_id,
                                )
                            )

                    model_record.fields[field_name] = field_value

            else:
                # нужно проверить, можно ли подставлять пустые значения
                model_field = model_record.model_class._meta.get_field(field_name)  # noqa

                if model_field.null:
                    field_value = 'None'

                elif model_field.blank:
                    field_value = '\'\''

                else:
                    raise ValueError(
                        f'A value for field {field_name} in model {model_label}'
                        f' must be provided in the fixture!'
                    )

                model_record.fields[field_name] = field_value

    def get_record(
        self,
        model_label: str,
        record_pk: str,
    ):
        """
        Метод получения записи их хранилища
        """
        key = (
            model_label,
            record_pk,
        )

        return self._records[key]

    def get_dependencies_for_record_by_fk_recursively(
        self,
        preparing_model_record: PreparingModelRecord,
        result: Optional[List[PreparingModelRecord]] = None,
    ) -> List[PreparingModelRecord]:
        """Формирует список зависимостей для записи модели на основе fk-полей (рекурсивно).

        Args:
            preparing_model_record: Запись модели, для которой нужно сформировать список зависимостей,
            result: Рекурсивно наполняемый список.

        Returns:
            Список записей моделей.

        """
        if result is None:
            result = []
        else:
            result.append(preparing_model_record)

        model_record: ModelRecord = preparing_model_record.model_record
        existing_factory: ExistingFactory = self._model_factory_correlation_storage.get_existing_factory(
            model_record.model_label
        )

        if model_record.fk_field_names:
            for field_name in model_record.fk_field_names:
                if (
                    model_record.fields[field_name] == 'None' or
                    field_name not in existing_factory.get_or_create_fields
                ):
                    continue

                if isinstance(model_record.fields[field_name], str):
                    foreign_preparing_model_record = self.get_record(
                        model_record.foreign_key_fields_map[field_name],
                        model_record.fields[field_name]
                    )
                else:
                    foreign_preparing_model_record = model_record.fields[field_name]

                self.get_dependencies_for_record_by_fk_recursively(
                    foreign_preparing_model_record,
                    result=result,
                )

        return result

    def add(
        self,
        model_record: ModelRecord,
        tag: int,
        is_add_recursively_fks: bool = False,
        use_factory_get_or_create_fields: bool = False,
        changed_fields: Optional[Dict[str, Any]] = None,
        is_update_model_record: bool = False,
    ) -> PreparingModelRecord:
        """
        Добавление/обновление обрабатываемой записи в хранилище. При необходимости можно
        указать, чтобы в хранилище были добавлены все ссылки на внешние объекты
        в хранилище.
        """
        key = model_record.key

        if key in self._records:
            preparing_model_record = self._records[key]

            if is_update_model_record:
                preparing_model_record.model_record = model_record
            else:
                preparing_model_record.set_tag(
                    tag=tag,
                    changed_fields=changed_fields,
                )
        else:
            preparing_model_record = PreparingModelRecord(
                model_record=model_record,
                tag=tag,
                changed_fields=changed_fields,
            )

            self._records[key] = preparing_model_record

            if is_add_recursively_fks:
                model_default_factory = self._existing_factory_storage.get_model_default_factory(
                    model_record.model_label
                )

                for field_name in model_record.fk_field_names:
                    if (
                        use_factory_get_or_create_fields and
                        field_name not in model_default_factory.get_or_create_fields
                    ):
                        continue

                    field_value: Union[PreparingModelRecord, str] = (
                        model_record.fields[field_name]
                    )

                    if field_value != 'None':
                        self.add(
                            model_record=field_value.model_record,
                            tag=PreparingModelRecordTagEnum.GETTING,
                            is_add_recursively_fks=True,
                            use_factory_get_or_create_fields=use_factory_get_or_create_fields,
                        )

        return preparing_model_record

    def set_dependencies_recursively(
        self,
        model_record: ModelRecord,
        has_dependence: bool = False,
    ) -> PreparingModelRecord:
        """
        Рекурсивное проставление зависимостей для записей в хранилище,
        с учетом зависимости предыдущей(родительской) записи.
        """
        preparing_record = self._records[model_record.key]
        correlation_storage = self._model_factory_correlation_storage

        if not preparing_record.has_dependence:
            preparing_record.has_dependence = has_dependence
            factory = correlation_storage.get_existing_factory(
                model_label=model_record.model_label,
            )

            for field_name in model_record.fk_field_names:
                preparing_record_from_fk: Union[PreparingModelRecord, str] = (
                    model_record.fields[field_name]
                )

                if preparing_record.has_only_getting_tag:
                    has_dependence = (
                            field_name in factory.get_or_create_fields and
                            preparing_record.has_dependence
                    )
                elif preparing_record.has_creating_tag:
                    has_dependence = True

                elif preparing_record.has_deleting_tag:
                    has_dependence = field_name in factory.get_or_create_fields

                elif preparing_record.has_updating_tag:
                    has_dependence = field_name in factory.get_or_create_fields

                    if field_name in preparing_record.changed_fields:
                        changed_field_value: Union[PreparingModelRecord, str] = (
                            preparing_record.changed_fields[field_name]
                        )
                        self.set_dependencies_recursively(
                            model_record=changed_field_value.model_record,
                            has_dependence=True,
                        )

                if preparing_record_from_fk != 'None':
                    if model_record.foreign_key_fields_map[field_name] == (
                        CONTENT_TYPE_MODEL
                    ):
                        continue

                    self.set_dependencies_recursively(
                        model_record=preparing_record_from_fk.model_record,
                        has_dependence=has_dependence,
                    )

        return preparing_record

    def substitute_fk_ids(
        self,
        fk_source_storage: Optional['PreparingModelRecordStorage'] = None,
    ):
        """
        Замена полей внешних ключей с идентификаторов на объекты. Убирается
        суффикс _id и устанавливается значение. Если значение не найдено, то
        устанавливается 'None'.

        В параметрах можно передать fk_source_storage - хранилище, из которого
        должны проставляться значения внешних ключей. Если хранилище не
        передано, то значения будут браться из текущего хранилища. Это сделано
        для работы нахождения разницы состояний базы данных.

        Сама замена производится после наполнения хранилища записями
        """
        if not fk_source_storage:
            fk_source_storage = self

        for preparing_model_record in self._records.values():
            model_record = preparing_model_record.model_record

            self._fill_fk_fields(
                model_record=model_record,
                fk_source_storage=fk_source_storage,
                fk_field_model_label_map=model_record.foreign_key_fields_map,
            )

    def difference(
        self,
        storage: 'PreparingModelRecordStorage',
    ) -> 'PreparingModelRecordStorage':
        """
        Получает разницу двух хранилищ в виде нового хранилища со всеми
        зависимыми записями моделей
        """
        from factory_bo.actions import (
            DifferencePreparingModelRecordStorageAction,
        )

        difference_action = DifferencePreparingModelRecordStorageAction(
            begin_storage=storage,
            end_storage=self,
            model_factory_correlation_storage=(
                self._model_factory_correlation_storage
            ),
            existing_factory_storage=self._existing_factory_storage,
        )

        difference_storage = difference_action.run()

        return difference_storage

    def union(
        self,
        src_storage: 'PreparingModelRecordStorage',
    ) -> 'PreparingModelRecordStorage':
        """
        Объединение двух хранилищ. Считается, что хранилище, у которого вызван
        метод - является целевым и результирующее хранилище будет создано на
        его основе. В метод передается хранилище-донор, записи которого будут
        перемещены в результирующее хранилище.
        """
        from factory_bo.actions import (
            UnionPreparingModelRecordStorageAction,
        )

        union_action = UnionPreparingModelRecordStorageAction(
            dst_storage=self,
            src_storage=src_storage,
            model_factory_correlation_storage=(
                self._model_factory_correlation_storage
            ),
            existing_factory_storage=self._existing_factory_storage,
        )

        union_storage = union_action.run()

        return union_storage


class PreparingModelRecordStorageCreator(metaclass=ABCMeta):
    """
    Базовый класс для создания хранилищ кешей записей фабрик
    """

    def __init__(
        self,
        existing_factory_storage: ExistingFactoryStorage,
        *args,
        **kwargs,
    ):
        self._existing_factory_storage = existing_factory_storage
        self._content_type_cache: Dict[int, ContentType] = {
            ct.pk: ct
            for ct in ContentType.objects.all()
        }

    @abstractmethod
    def create(
        self,
        need_substitute_fk_ids: bool = False,
    ) -> PreparingModelRecordStorage:
        """
        Контрактный метод создания хранилища кешей фабрик
        """
        pass


class DefaultDBPreparingModelRecordStorageCreator(
    PreparingModelRecordStorageCreator,
):
    """
    Создатель хранилища кешей записей фабрик из дефолтной базы данных
    """

    def create(
        self,
        need_substitute_fk_ids: bool = False,
        fk_source_storage: Optional['PreparingModelRecordStorage'] = None,
        preparing_model_record_tag: int = PreparingModelRecordTagEnum.CREATING,
    ) -> PreparingModelRecordStorage:
        """
        Создание хранилища кешей фабрик и их наполнение
        """
        correlation_storage_creator = ModelFactoryCorrelationStorageCreator(
            existing_factory_storage=self._existing_factory_storage,
        )

        correlation_storage = correlation_storage_creator.create()

        preparing_model_record_storage = PreparingModelRecordStorage(
            model_factory_correlation_storage=correlation_storage,
            existing_factory_storage=self._existing_factory_storage,
        )
        model_storage = self._existing_factory_storage.model_storage

        for model in model_storage.get_model_classes():
            objects = self.get_model_objects(model)

            if objects:
                self.add_model_objects_to_storage(
                    model,
                    model_storage,
                    objects,
                    preparing_model_record_storage,
                    preparing_model_record_tag,
                )

        if need_substitute_fk_ids:
            preparing_model_record_storage.substitute_fk_ids(
                fk_source_storage=fk_source_storage,
            )

        return preparing_model_record_storage

    def update_storage(
        self,
        preparing_model_record_storage: Optional['PreparingModelRecordStorage'],
        changed_tables: set,
        need_substitute_fk_ids: bool = False,
        preparing_model_record_tag: int = PreparingModelRecordTagEnum.CREATING,
    ) -> PreparingModelRecordStorage:
        """
        Обновление хранилища кешей фабрик по списку таблиц.
        """
        model_storage = self._existing_factory_storage.model_storage

        for model in model_storage.get_model_classes():
            if changed_tables and model._meta.db_table not in changed_tables:
                continue

            objects = self.get_model_objects(model)

            if objects:
                self.add_model_objects_to_storage(
                    model,
                    model_storage,
                    objects,
                    preparing_model_record_storage,
                    preparing_model_record_tag,
                    is_update_model_record=True,
                )

        if need_substitute_fk_ids:
            preparing_model_record_storage.substitute_fk_ids()

        return preparing_model_record_storage

    def get_model_objects(
        self,
        model: Type[Model],
    ) -> list:
        """
        Получить все объекты модели используя базовый менеджер.
        """
        with substitute_model_get_queryset_method(model):
            try:
                objects = list(model.objects.order_by('pk'))
            except Exception as e:
                objects = []
                print(f'model "{model.__name__}" failed due to: {e}')

        return objects

    def add_model_objects_to_storage(
        self,
        model: Type[Model],
        model_storage: ModelStorage,
        objects: list,
        preparing_model_record_storage: PreparingModelRecordStorage,
        preparing_model_record_tag: int,
        is_update_model_record: bool = False,
    ):
        """
        Добавить запись объекта модели в хранилище и удалить из хранилища лишние записи.

        Args:
            model: Django-модель
            model_storage: Хранилище моделей
            objects: QuerySet-объектов модели
            preparing_model_record_storage: Хранилище записей моделей
            preparing_model_record_tag: Тег для указания в preparing_model_record
            is_update_model_record: Ключ требуется ли обновить запись model_record
        """
        exists_model_record_keys = {
            key
            for key in preparing_model_record_storage.records.keys()
            if key[0] == model._meta.label
        }
        model_fk_fields_map = model_storage.get_model_foreign_key_fields_map(
            model_label=model._meta.label,
        )
        allowed_fields = model_storage.get_allowed_fields(
            model_label=model._meta.label,
        )

        for object_ in objects:
            model_record = self.prepare_model_record(
                model,
                model_fk_fields_map,
                allowed_fields,
                object_,
            )
            if model_record.key in exists_model_record_keys:
                exists_model_record_keys.remove(model_record.key)

            preparing_model_record_storage.add(
                model_record=model_record,
                tag=preparing_model_record_tag,
                is_update_model_record=is_update_model_record,
            )

        if exists_model_record_keys:
            # Удалим значения по оставшимся ключам, т.к. не были найдены соответствующие объекты модели.
            for key in exists_model_record_keys:
                preparing_model_record_storage.records.pop(key)

    def prepare_model_record(
        self,
        model: Type[Model],
        model_fk_fields_map: Dict[str, str],
        allowed_fields: Optional[List[Field]],
        object_
    ) -> ModelRecord:
        """
        Подготовка Записи модели
        """
        fields = {}

        for field in allowed_fields:
            if field.__class__.__name__ in EXCLUDED_FIELD_CLASSES:
                fields[field.attname] = 'None'
            else:
                field_value = getattr(object_, field.attname)

                if (
                    isinstance(field, UUIDField) and
                    field_value is not None
                ):
                    field_value = repr(str(field_value))
                elif (field.primary_key or isinstance(field, ForeignKey)) and isinstance(field_value, str):
                    # строковые значения PK и FK не преобразовываем
                    pass
                else:
                    field_value = repr(field_value)

                fields[field.attname] = field_value

        model_record = ModelRecord(
            model_class=model,
            foreign_key_fields_map=model_fk_fields_map,
            fields=fields,
            content_type_cache=self._content_type_cache,
        )
        return model_record


class JSONPreparingModelStorageCreator(PreparingModelRecordStorageCreator):
    """
    Создатель хранилища кешей записей тестовых фабрик из переданного контента
    json-файла
    """

    def __init__(
        self,
        factories_json: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._models_dict = json.loads(factories_json)

    def create(
        self,
        need_substitute_fk_ids: bool = False,
        fk_source_storage: Optional['PreparingModelRecordStorage'] = None,
        preparing_model_record_tag: int = PreparingModelRecordTagEnum.CREATING,
    ) -> PreparingModelRecordStorage:
        """
        Создание хранилища кешей с заполнением записей из переданного контента
        """
        correlation_storage_creator = ModelFactoryCorrelationStorageCreator(
            existing_factory_storage=self._existing_factory_storage,
        )

        correlation_storage = correlation_storage_creator.create()

        preparing_model_record_storage = PreparingModelRecordStorage(
            model_factory_correlation_storage=correlation_storage,
            existing_factory_storage=self._existing_factory_storage,
        )

        for model_label, models_list in self._models_dict.items():
            model_class = self._existing_factory_storage.model_storage.get_model_class(  # noqa
                model_label=model_label,
            )

            # Модели не находящиеся в хранилище не соответствуют предъявляемым
            # требованиям
            if not model_class:
                continue

            for model_fields in models_list:
                model_record = ModelRecord(
                    model_class=model_class,
                    foreign_key_fields_map=self._existing_factory_storage.model_storage.get_model_foreign_key_fields_map(  # noqa
                        model_label=model_label,
                    ),
                    fields=model_fields,
                    content_type_cache=self._content_type_cache,
                )

                preparing_model_record_storage.add(
                    model_record=model_record,
                    tag=preparing_model_record_tag,
                )

        if need_substitute_fk_ids:
            preparing_model_record_storage.substitute_fk_ids(
                fk_source_storage=fk_source_storage,
            )

        return preparing_model_record_storage


class ModelFactoryCorrelationStorage:
    """
    Хранилище соответствий моделей и фабрик
    """

    def __init__(
        self,
        correlation_map: Optional[Dict[str, ExistingFactory]],
    ):
        self._correlation_map = correlation_map or {}

    def get_existing_factory(
        self,
        model_label: str,
    ):
        """
        Метод получения фабрики для модели
        """
        return self._correlation_map[model_label]


class ModelFactoryCorrelationStorageCreator:
    """
    Создатель хранилищ соответствий моделей и фабрик. Упрощает работу с
    созданием хранилища, т.к. заблаговременно создается дефолтная карта
    соответствия моделей и фабрик.
    """

    def __init__(
        self,
        existing_factory_storage: ExistingFactoryStorage,
    ):
        self._existing_factory_storage = existing_factory_storage

        self._default_correlation_map = (
            self._existing_factory_storage.get_model_default_factory_map()
        )

    def create(
        self,
        custom_correlation_map: Optional[Dict[str, str]] = None,
    ):
        """
        Фабричный метод создания хранилища соответствия моделей и фабрик с
        поправкой на кастомные значения
        """
        correlation_map = copy(self._default_correlation_map)

        if custom_correlation_map:
            for model_label, factory_class_name in custom_correlation_map.items():  # noqa
                factory = self._existing_factory_storage.get_factory_class_for_model(  # noqa
                    model_label=model_label,
                    factory_class_name=factory_class_name,
                )

                correlation_map[model_label] = factory

        return ModelFactoryCorrelationStorage(
            correlation_map=correlation_map,
        )
