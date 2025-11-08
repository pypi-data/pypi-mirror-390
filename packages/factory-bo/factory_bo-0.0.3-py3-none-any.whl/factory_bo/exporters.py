import json
import os
from abc import (
    abstractmethod,
)
from collections import (
    defaultdict,
)
from datetime import (
    datetime,
)
from itertools import (
    groupby,
)
from operator import (
    itemgetter,
)
from typing import (
    Iterable,
    List,
    Optional,
    Set,
)

from django.conf import (
    settings,
)
from isort.api import (
    sort_code_string,
)

from factory_bo.consts import (
    FACTORY_CLASS_NAME_DELIMETER,
    IMPORT_TEMPLATE,
    IMPORT_WITH_ALIAS_TEMPLATE,
    MODEL_CLASS_NAME_ID_DELIMITER,
    TAB_STR,
)
from factory_bo.enums import (
    PreparingModelRecordTagEnum,
    UsingLibraryEnum,
)
from factory_bo.helpers import (
    get_pk_slug,
    is_pseudo_fk_field,
)
from factory_bo.mixins import (
    BaseExporter,
    PreparingModelSortMixin,
)
from factory_bo.records import (
    PreparingModelRecord,
)
from factory_bo.storages import (
    ExistingFactoryStorage,
    ModelFactoryCorrelationStorage,
    PreparingModelRecordStorage,
)
from factory_bo.strings import (
    PYTHON_FIXTURE_PATH_HAVE_NOT_PY_EXTENSION_ERROR,
)


class PreparingModelRecordStorageExporter(BaseExporter):
    """
    Базовый класс экспортев хранилища в файл
    """

    def __init__(
        self,
        preparing_model_record_storage: PreparingModelRecordStorage,
        existing_factory_storage: ExistingFactoryStorage,
    ):
        self._preparing_model_record_storage = preparing_model_record_storage
        self._existing_factory_storage = existing_factory_storage

    @abstractmethod
    def to_string(
        self,
        *args,
        **kwargs,
    ) -> str:
        pass


class BasePyExporter(BaseExporter):
    """
    Базовый Python-экспортер
    """

    @abstractmethod
    def _get_function_declaration(self) -> str:
        """
        Возвращает строку объявления функции
        """
        pass

    def _prepare_libraries_imports(
        self,
        content: str,
    ) -> List[str]:
        """
        Подготавливает импорты библиотек
        """
        libraries_imports = []

        for key_word in UsingLibraryEnum.values.keys():
            if key_word in content:
                libraries_imports.append(
                    UsingLibraryEnum.values[key_word]
                )

        return libraries_imports

    def _prepare_imports(
        self,
        content: str,
    ) -> List[str]:
        libraries_imports = self._prepare_libraries_imports(
            content=content,
        )

        imports = [
            *libraries_imports,
        ]

        return imports

    def _add_imports(
        self,
        content: str,
    ) -> str:
        """
        Добавление и сортировка импортов
        """
        imports = self._prepare_imports(
            content=content,
        )

        content_with_imports = '\n'.join(
            [
                *imports,
                content,
            ]
        )

        return content_with_imports

    def _sort_imports(
        self,
        content: str,
    ):
        """
        Сортировка импортов при помощи isort
        """
        return sort_code_string(
            code=content,
            config=settings.ISORT_CONFIG,
        )

    def _prepare_function_components(self) -> List[str]:
        """
        Подготавливает составляющие функции для дальнейшей конкатинации
        """
        components = [
            self._get_function_declaration(),
        ]

        return components

    def _prepare_function_loader_content(self) -> str:
        """
        Генерирует исходный код функции загрузки предыстории
        """
        components = self._prepare_function_components()

        pre_content = []

        for component in components:
            if component:
                pre_content.extend([component, ''])

        content = '\n'.join(pre_content)

        return content

    def to_string(
        self,
        *args,
        **kwargs,
    ) -> str:
        """
        Возвращает строку содержащую функцию factory_loader с фабриками в тебе
        и импортами всех необходимых фабрик и классов сторонних библиотек
        """
        content = self._prepare_function_loader_content()

        content = self._add_imports(
            content=content,
        )

        content = self._sort_imports(
            content=content,
        )

        return content

    def to_file(
        self,
        *args,
        file_path: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Формирование Python-фикстуры
        """
        if not file_path.endswith('.py'):
            raise ValueError(
                PYTHON_FIXTURE_PATH_HAVE_NOT_PY_EXTENSION_ERROR.format(
                    fixture_path=file_path,
                )
            )

        return super().to_file(
            *args,
            file_path=file_path,
            **kwargs,
        )


class PyFactoryExporter(
    BasePyExporter,
    PreparingModelSortMixin,
    PreparingModelRecordStorageExporter,
):
    """
    Экспортер фабрик в виде Python-фикстуры
    """

    def __init__(
        self,
        model_factory_correlation_storage: ModelFactoryCorrelationStorage,
        *args,
        **kwargs,
    ):
        self._model_factory_correlation_storage = model_factory_correlation_storage
        self._factory_imports = set()
        self._already_existing_records = []

        super().__init__(*args, **kwargs)

    def _check_getting_record_dependency(
        self,
        preparing_record: PreparingModelRecord,
    ):
        """
        Проверяет, является ли запись только для выборки и есть ли от нее
        зависимые
        """
        return (
            preparing_record.has_only_getting_tag and
            not preparing_record.has_dependence
        )

    def _get_preparing_factories(
        self,
        sorted_preparing_record_model_ids: List[str],
    ) -> str:
        """
        Получение обрабатываемых записей - получаемых и создаваемых в строковом
        представлении
        """
        preparing_factory_strs = []
        deferred_save_fields = defaultdict(list)

        for record_model_id in sorted_preparing_record_model_ids:
            model_label, model_record_pk = record_model_id.split(MODEL_CLASS_NAME_ID_DELIMITER)

            preparing_record = self._preparing_model_record_storage.records.get(
                (
                    model_label,
                    model_record_pk,
                )
            )

            record_fields = {}
            existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                model_label=preparing_record.model_record.model_label,
            )

            # Пропустим получаемые(и только получаемые) записи, для которых
            # нет зависимой записи, чтобы не формировать неиспользуемые
            # переменные и фабрики в фикстуре
            if self._check_getting_record_dependency(preparing_record):
                continue

            self._factory_imports.add(
                (
                    existing_factory.import_path,
                    existing_factory.factory_class_name,
                )
            )

            if preparing_record.has_creating_tag:
                field_names = preparing_record.model_record.fields.keys()
            elif preparing_record.has_getting_tag:
                field_names = existing_factory.get_or_create_fields
            else:
                field_names = []

            if (
                existing_factory.allow_use_id_field and
                'id' in preparing_record.model_record.all_fields
            ):
                field_names = preparing_record.model_record.all_fields.keys()
                model_record_fields = preparing_record.model_record.all_fields
            else:
                model_record_fields = preparing_record.model_record.fields

            existing_factory_class = existing_factory.factory_class_name

            if preparing_record.has_getting_tag:
                variable_name = f'{existing_factory_class.lower()}_{get_pk_slug(preparing_record.model_record.pk)}'

            for field_name in field_names:
                if field_name in existing_factory.auto_updated_fields:
                    continue

                field_value = model_record_fields[field_name]

                if isinstance(field_value, PreparingModelRecord):
                    fk_existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                        model_label=field_value.model_record.model_label,
                    )

                    self._factory_imports.add(
                        (
                            fk_existing_factory.import_path,
                            fk_existing_factory.factory_class_name,
                        )
                    )

                    field_value = (
                        f'{fk_existing_factory.factory_class_name.lower()}_'
                        f'{get_pk_slug(field_value.model_record.pk)}'
                    )

                    # Сохраняем поля для отложенного сохранения после добавления
                    # связанных объектов.
                    if preparing_record.has_getting_tag:
                        if field_name in existing_factory.excluded_fk_fields:
                            deferred_save_fields[field_value].append(
                                (
                                    variable_name,
                                    field_name,
                                )
                            )
                            continue

                    try:
                        # Исключим поля CompositeForeignKey
                        from compositefk.fields import (
                            CompositeForeignKey,
                        )
                        field_obj = preparing_record.model_record.model_class._meta.get_field(field_name)

                        if not isinstance(field_obj, CompositeForeignKey):
                            field_value = f'{field_value}.pk'
                    except ImportError:
                        field_value = f'{field_value}.pk'

                record_fields[field_name] = field_value

            formatted_fields = ''.join(
                [
                    f"{TAB_STR * 2}{k}={v},\n"
                    for k, v in record_fields.items()
                ]
            )

            if preparing_record.has_getting_tag:
                record_str = (
                    f'{TAB_STR}{variable_name} = {existing_factory_class}(\n'
                    f'{formatted_fields}{TAB_STR})'
                )
            else:
                record_str = (
                    f'{TAB_STR}{existing_factory_class}(\n'
                    f'{formatted_fields}{TAB_STR})'
                )
            if record_str not in self._already_existing_records:
                preparing_factory_strs.append(record_str)
                self._already_existing_records.append(record_str)

            # Проверяем нет ли связанных объектов с полями отложенного
            # сохранения, если есть, то добавляем в них и сохраняем.
            if preparing_record.has_getting_tag:
                related_objects = deferred_save_fields.get(variable_name)
                if related_objects:
                    for deferred_object, object_fields in groupby(
                        related_objects,
                        key=itemgetter(0)
                    ):
                        deferred_fields = []
                        for _, field in object_fields:
                            deferred_fields.append(
                                f'{TAB_STR}{deferred_object}.{field} = '
                                f'{variable_name}.pk'
                            )
                        deferred_fields.append(
                            f'{TAB_STR}{deferred_object}.save()'
                        )

                        preparing_factory_strs.append(
                            '\n'.join(deferred_fields)
                        )

        return '\n'.join(preparing_factory_strs)

    def _get_getting_factories(self) -> str:
        """
        Получение всех запрашиваемых записей фабрик в строковом представлении
        """
        getting_records: List[PreparingModelRecord] = list(
            filter(
                lambda record: (
                    PreparingModelRecordTagEnum.GETTING in record.tags and
                    PreparingModelRecordTagEnum.CREATING not in record.tags
                ),
                self._preparing_model_record_storage.records.values()
            )
        )

        sorted_getting_record_model_ids = self._sort_records(
            records=getting_records,
        )

        return self._get_preparing_factories(
            sorted_preparing_record_model_ids=sorted_getting_record_model_ids,
        )

    def _get_creating_factories(self) -> str:
        """
        Получение всех создаваемых записей фабрик в строковом представлении
        """
        creating_records: List[PreparingModelRecord] = list(
            filter(
                lambda record: (
                    PreparingModelRecordTagEnum.CREATING in record.tags
                ),
                self._preparing_model_record_storage.records.values()
            )
        )

        sorted_creating_record_model_ids = self._sort_records(
            records=creating_records,
        )

        return self._get_preparing_factories(
            sorted_preparing_record_model_ids=sorted_creating_record_model_ids,
        )

    def _get_updating_factories(self) -> str:
        """
        Получение всех обновляемых записей фабрик в строковом представлении
        """
        updating_records: List[PreparingModelRecord] = list(
            filter(
                lambda record: (
                    PreparingModelRecordTagEnum.UPDATING in record.tags
                ),
                self._preparing_model_record_storage.records.values()
            )
        )

        sorted_updating_record_model_ids = self._sort_records(
            records=updating_records,
        )

        updating_factory_strs = []

        for record_model_id in sorted_updating_record_model_ids:
            model_label, model_record_pk = record_model_id.split(MODEL_CLASS_NAME_ID_DELIMITER)
            preparing_record = self._preparing_model_record_storage.records.get(
                (
                    model_label,
                    model_record_pk,
                )
            )

            if PreparingModelRecordTagEnum.UPDATING not in preparing_record.tags:
                # такая запись могла попасть сюда после сортировки, которая
                # добавляет в обрабатываемый список записей зависимости
                continue

            record_fields = []
            existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                model_label=preparing_record.model_record.model_label,
            )
            self._factory_imports.add(
                (
                    existing_factory.import_path,
                    existing_factory.factory_class_name,
                )
            )

            for field_name, field_value in preparing_record.changed_fields.items():
                if isinstance(field_value, PreparingModelRecord):
                    fk_existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                        model_label=field_value.model_record.model_label,
                    )

                    self._factory_imports.add(
                        (
                            fk_existing_factory.import_path,
                            fk_existing_factory.factory_class_name,
                        )
                    )

                    field_value = (
                        f'{fk_existing_factory.factory_class_name.lower()}_'
                        f'{get_pk_slug(field_value.model_record.pk)}'
                    )

                    if is_pseudo_fk_field(field_name):
                        field_value = f'{field_value}.id'

                record_fields.append(
                    (
                        field_name,
                        field_value,
                    )
                )

            existing_factory_class = existing_factory.factory_class_name

            variable_name = (
                f'{existing_factory_class.lower()}_'
                f'{get_pk_slug(preparing_record.model_record.pk)}'
            )

            formatted_fields = ''.join(
                [
                    f"{TAB_STR}{variable_name}.{k} = {v}\n"
                    for (k, v) in record_fields
                ]
            )

            record_str = (
                f'{formatted_fields}'
                f'{TAB_STR}{variable_name}.save()'
            )

            updating_factory_strs.append(record_str)

        return '\n'.join(updating_factory_strs)

    def _get_deleting_factories(self) -> str:
        """
        Получение всех удаляемых записей фабрик в строковом представлении
        """
        deleting_records: List[PreparingModelRecord] = list(
            filter(
                lambda record: (
                    PreparingModelRecordTagEnum.DELETING in record.tags
                ),
                self._preparing_model_record_storage.records.values()
            )
        )

        sorted_deleting_record_model_ids = self._sort_records(
            records=deleting_records,
            is_reversed=False,
        )

        deleting_factory_strs = []

        for record_model_id in sorted_deleting_record_model_ids:
            model_label, model_record_pk = record_model_id.split(MODEL_CLASS_NAME_ID_DELIMITER)
            preparing_record = self._preparing_model_record_storage.records.get(
                (
                    model_label,
                    model_record_pk,
                )
            )

            if not preparing_record.has_deleting_tag:
                continue

            existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                model_label=preparing_record.model_record.model_label,
            )

            existing_factory_class_name = existing_factory.factory_class_name

            self._factory_imports.add(
                (
                    existing_factory.import_path,
                    existing_factory_class_name,
                )
            )

            variable_name = (
                f'{existing_factory_class_name.lower()}_'
                f'{get_pk_slug(preparing_record.model_record.pk)}'
            )

            record_str = f'{TAB_STR}{variable_name}.delete()'

            deleting_factory_strs.append(record_str)

        return '\n'.join(deleting_factory_strs)

    def _get_function_declaration(self) -> str:
        """
        Возвращает строку объявления функции загрузки
        """
        return 'def factory_loader(context):'

    def _prepare_factory_imports(self) -> List[str]:
        """
        Подготовливает импорты фабрик
        """
        factory_imports = []

        for import_path, factory_class_name in self._factory_imports:
            if FACTORY_CLASS_NAME_DELIMETER in factory_class_name:
                factory_class_name_alias = factory_class_name
                factory_class_name = factory_class_name.split(FACTORY_CLASS_NAME_DELIMETER)[0]

                import_string = IMPORT_WITH_ALIAS_TEMPLATE.format(
                    import_path=import_path,
                    class_name=factory_class_name,
                    class_name_alias=factory_class_name_alias,
                )
            else:
                import_string = IMPORT_TEMPLATE.format(
                    import_path=import_path,
                    class_name=factory_class_name,
                )

            factory_imports.append(import_string)

        return factory_imports

    def _prepare_imports(
        self,
        content: str,
    ) -> List[str]:
        factory_imports = self._prepare_factory_imports()

        parent_imports = super()._prepare_imports(content)

        imports = [
            *factory_imports,
            *parent_imports,
        ]

        return imports

    def _prepare_function_components(self) -> List[str]:
        """
        Подготавливает составляющие функции для дальнейшей конкатинации
        """
        components = [
            self._get_function_declaration(),
            self._get_getting_factories(),
            self._get_creating_factories(),
            self._get_updating_factories(),
            self._get_deleting_factories(),
        ]

        return components

    def _prepare_file_path(self) -> str:
        """
        Формирует абсолютный путь будущей Python-фикстуры
        """
        now_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        result_dir_name = 'diff_result'

        result_file_name = f'diff_fixtures__{now_str}.py'

        result_dir_path = os.path.join(
            settings.FACTORY_BO__FIXTURES_DIR_PATH,
            result_dir_name
        )
        if not os.path.exists(result_dir_path):
            os.mkdir(result_dir_path)

        file_path = os.path.join(
            result_dir_path,
            result_file_name
        )

        return file_path

    def to_file(
        self,
        *args,
        file_path: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Формирование Python-фикстуры
        """
        if not file_path:
            file_path = self._prepare_file_path()

        return super().to_file(
            *args,
            file_path=file_path,
            **kwargs,
        )


class JSONModelExporter(PreparingModelRecordStorageExporter):
    """
    Экспортер обрабатываемых записей хранилища в формате JSON
    """

    def to_string(
        self,
        *args,
        exporting_model_labels: Optional[Set[str]] = None,
        **kwargs,
    ) -> str:
        """
        Вывод обрабатываемых создаваемых записей хранилища в виде JSON-строки
        """
        model_records = defaultdict(list)

        for (model_label, pk), preparing_model_record in self._preparing_model_record_storage.records.items():
            # В результирующий JSON должны попасть записи интересующих моделей
            if exporting_model_labels and model_label not in exporting_model_labels:
                continue

            if PreparingModelRecordTagEnum.CREATING in preparing_model_record.tags:
                model_records[model_label].append(
                    preparing_model_record.model_record.all_fields
                )

        return json.dumps(model_records) if model_records else None


class HierarchyForRecordsPyFactoryExporter(PyFactoryExporter):
    """
    Экспортер фабрик в виде Python-фикстуры для переданных записей моделей.
    """

    def _check_getting_record_dependency(
        self,
        preparing_record: PreparingModelRecord,
    ):
        """Всегда возвращает False, определяя запись как требующую создания переменной."""

        return False

    def to_string(
        self,
        preparing_model_records: Iterable[PreparingModelRecord],
        with_imports: Optional[bool] = False,
        *args,
        **kwargs,
    ) -> str:
        """Формирует python-код с фабриками на основе переданных моделей.

        Args:
            preparing_model_records: Итерируемый объект с моделями.
            with_imports: Добавлять ли в строку импорты.

        Returns:
            Python-код с фабриками.

        """
        sorted_record_model_ids = self._sort_records(preparing_model_records)

        factory_records_string = self._get_preparing_factories(
            sorted_preparing_record_model_ids=sorted_record_model_ids,
        )

        result_string = ''
        for row in factory_records_string.split('\n'):
            result_string += f'{row.removeprefix(" " * 4)}\n'

        if with_imports:
            imports_string = self._add_imports(content='')
            imports_string = self._sort_imports(content=imports_string)
            result_string = f'{imports_string}\n\n{result_string}'

        return result_string
