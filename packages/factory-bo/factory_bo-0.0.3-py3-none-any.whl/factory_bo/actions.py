from collections import (
    Iterable,
)
from copy import (
    deepcopy,
)
from random import (
    randint,
)
from typing import (
    Dict,
    Optional,
    Tuple,
)

from django.core.exceptions import (
    ValidationError,
)

from factory_bo.consts import (
    MODEL_CLASS_NAME_ID_DELIMITER,
    PK_OFFSET,
)
from factory_bo.enums import (
    PreparingModelRecordTagEnum,
)
from factory_bo.factories import (
    ExistingFactory,
)
from factory_bo.mixins import (
    PreparingModelSortMixin,
)
from factory_bo.records import (
    PreparingModelRecord,
)
from factory_bo.storages import (
    ExistingFactoryStorage,
    ModelFactoryCorrelationStorage,
    ModelFactoryCorrelationStorageCreator,
    PreparingModelRecordStorage,
)
from factory_bo.strings import (
    NON_UNIQUE_DJANGO_GET_OR_CREATE_RECORD_FOUND_ERROR,
)


class DifferencePreparingModelRecordStorageAction(PreparingModelSortMixin):
    """
    Служит для нахождения разницы состояний записей хранилищ. Результатом
    работы является новое хранилище, содержащее разницу между двумя хранилищами
    """
    def __init__(
        self,
        begin_storage: PreparingModelRecordStorage,
        end_storage: PreparingModelRecordStorage,
        model_factory_correlation_storage: ModelFactoryCorrelationStorage,
        existing_factory_storage: ExistingFactoryStorage,
    ):
        self._begin_storage = begin_storage
        self._end_storage = end_storage
        self._model_factory_correlation_storage = (
            model_factory_correlation_storage
        )
        self._existing_factory_storage = existing_factory_storage

    def _find_creating_difference(
        self,
        difference_storage: PreparingModelRecordStorage,
        begin_storage: PreparingModelRecordStorage,
        end_storage: PreparingModelRecordStorage,
    ):
        """
        Поиск и добавление создаваемых записей
        """
        different_record_keys = set(end_storage.records.keys()).difference(
            begin_storage.records.keys()
        )

        for key in different_record_keys:
            preparing_model_record = end_storage.records[key]

            difference_storage.add(
                model_record=preparing_model_record.model_record,
                tag=PreparingModelRecordTagEnum.CREATING,
                is_add_recursively_fks=True,
            )

    def _find_updating_difference(
        self,
        difference_storage: PreparingModelRecordStorage,
        begin_storage: PreparingModelRecordStorage,
        end_storage: PreparingModelRecordStorage,
    ):
        """
        Поиск и добавление обновляемых записей
        """
        intersection_record_keys = set(end_storage.records.keys()).intersection(
            begin_storage.records.keys()
        )

        for key in intersection_record_keys:
            begin_preparing_model_record = begin_storage.records.get(key)
            end_preparing_model_record = end_storage.records.get(key)

            if begin_preparing_model_record and end_preparing_model_record:
                changed_fields = {}

                field_names = begin_preparing_model_record.model_record.fields.keys()  # noqa

                for field_name in field_names:
                    begin_field_value = begin_preparing_model_record.model_record.fields[field_name]  # noqa
                    end_field_value = end_preparing_model_record.model_record.fields[field_name]  # noqa

                    if begin_field_value != end_field_value:
                        changed_fields[field_name] = end_field_value

                        if isinstance(end_field_value, PreparingModelRecord):
                            difference_storage.add(
                                model_record=end_field_value.model_record,
                                tag=PreparingModelRecordTagEnum.GETTING,
                                is_add_recursively_fks=True,
                            )

                if changed_fields:
                    difference_storage.add(
                        model_record=begin_preparing_model_record.model_record,
                        tag=PreparingModelRecordTagEnum.UPDATING,
                        is_add_recursively_fks=True,
                        changed_fields=changed_fields,
                    )

    def _find_deleting_difference(
        self,
        difference_storage: PreparingModelRecordStorage,
        begin_storage: PreparingModelRecordStorage,
        end_storage: PreparingModelRecordStorage,
    ):
        """
        Поиск и обновление удаляемых записей
        """
        different_record_keys = set(begin_storage.records.keys()).difference(
            end_storage.records.keys()
        )

        for key in different_record_keys:
            preparing_model_record = begin_storage.records[key]

            difference_storage.add(
                model_record=preparing_model_record.model_record,
                tag=PreparingModelRecordTagEnum.DELETING,
                is_add_recursively_fks=True,
            )

    def _set_dependencies(
        self,
        difference_storage: PreparingModelRecordStorage,
    ):
        """
        Указание зависимостей в записях
        """
        for preparing_model_record in difference_storage.records.values():
            difference_storage.set_dependencies_recursively(
                model_record=preparing_model_record.model_record,
            )

    def run(self) -> PreparingModelRecordStorage:
        """
        Получает разницу двух хранилищ в виде нового хранилища со всеми
        зависимыми записями моделей
        """
        correlation_storage_creator = ModelFactoryCorrelationStorageCreator(
            existing_factory_storage=self._existing_factory_storage,
        )

        correlation_storage = correlation_storage_creator.create()

        difference_storage = PreparingModelRecordStorage(
            model_factory_correlation_storage=correlation_storage,
            existing_factory_storage=self._existing_factory_storage,
        )

        self._find_creating_difference(
            difference_storage=difference_storage,
            begin_storage=self._begin_storage,
            end_storage=self._end_storage,
        )

        self._find_updating_difference(
            difference_storage=difference_storage,
            begin_storage=self._begin_storage,
            end_storage=self._end_storage,
        )

        self._find_deleting_difference(
            difference_storage=difference_storage,
            begin_storage=self._begin_storage,
            end_storage=self._end_storage,
        )

        self._set_dependencies(
            difference_storage=difference_storage,
        )

        return difference_storage


class UnionPreparingModelRecordStorageAction(PreparingModelSortMixin):
    """
    Действие объединения двух хранилищ - целевого (dst_storage) и донора (
    src_storage), с подготовленными записями моделей

    Объединение хранилищ производится по следующему алгоритму:

    1) Создается полная копия целевого хранилища и сохраняется в качестве
        результирующего;
    2) Производится сортировка записей хранилища-донора по возрастанию степени
        зависимости записей;
    3) Производится добавление записей хранилище-донор. При переносе записи
        производится подмена идентификаторов записей во внешних ключей из
        таблицы соответствия. В качестве внешнего хранилища указывается
        результирующее хранилище;
    4) В результате должено быть получено объединенное результирующее хранилище.
    """
    def __init__(
        self,
        dst_storage: PreparingModelRecordStorage,
        src_storage: PreparingModelRecordStorage,
        model_factory_correlation_storage: ModelFactoryCorrelationStorage,
        existing_factory_storage: ExistingFactoryStorage,
    ):
        self._dst_storage = dst_storage
        self._src_storage = src_storage
        self._result_storage: Optional[PreparingModelRecordStorage] = None
        self._model_factory_correlation_storage = (
            model_factory_correlation_storage
        )
        self._existing_factory_storage = existing_factory_storage
        self._model_default_factory_map: Dict[str, ExistingFactory] = (
            self._existing_factory_storage.get_model_default_factory_map()
        )

        self._table_conformity: Dict[Tuple[str, str], PreparingModelRecord] = {}
        self._preparing_result_model_records_map: Dict[Tuple[str, Tuple[str, ...]], Tuple[str, str]] = {}  # noqa

    def _prepare_result_storage(self):
        """
        Создание результирующего хранилища
        """
        self._result_storage = deepcopy(self._dst_storage)

        # Все записи нужно пометить для выборки
        for record in self._result_storage.records.values():
            self._result_storage.add(
                model_record=record.model_record,
                tag=PreparingModelRecordTagEnum.GETTING,
            )

    def _get_unique_preparing_model_record_key(
        self,
        record: PreparingModelRecord,
    ):
        """
        Рекурсивное получение уникального ключа обрабатываемой записи модели.
        Если в наборе полей django_get_or_create фабрики присутствуют внешние
        ключи, и в качестве значений указаны экземпляры PreparingModelRecord, то
        необходимо для них получить уникальный ключ
        """
        existing_factory = (
            self._model_default_factory_map[record.model_record.model_label]
        )
        get_or_create_key_getter = (
            existing_factory.factory_class.get_django_get_or_create_getter()
        )
        record_get_or_create_key = []

        key_items = get_or_create_key_getter(record.model_record.all_fields)

        if not isinstance(key_items, Iterable) or isinstance(key_items, str):
            key_items = [
                key_items,
            ]

        for key_item in key_items:
            if isinstance(key_item, PreparingModelRecord):
                key_item = self._get_unique_preparing_model_record_key(
                    record=key_item,
                )

            record_get_or_create_key.append(key_item)

        return tuple(record_get_or_create_key)

    def _prepare_preparing_result_model_records_map(self):
        """
        Подготовка карты соответствия набора значений записей полей
        django_get_or_create и идентификатора
        """
        for (model_label, record_id), record in self._result_storage.records.items():  # noqa
            existing_factory = self._model_default_factory_map[model_label]
            model_get_or_create_key = (
                model_label,
                self._get_unique_preparing_model_record_key(
                    record=record,
                ),
            )

            if model_get_or_create_key in self._preparing_result_model_records_map:  # noqa
                raise ValidationError(
                    NON_UNIQUE_DJANGO_GET_OR_CREATE_RECORD_FOUND_ERROR.format(
                        factory_class_name=existing_factory.factory_class_name,
                        key=model_get_or_create_key,
                    )
                )

            self._preparing_result_model_records_map[model_get_or_create_key] = (  # noqa
                model_label,
                record_id,
            )

    def _recalculate_src_storage_record_pks(self):
        """
        Перед объединением двух хранилищ, необходимо произвести сдвиг всех
        идентификаторов на константное значение для избежания коллизий при
        появлении разных записей с одинаковыми идентификаторами
        """
        replace_keys_map = {}

        src_records = self._src_storage.records

        for (model_label, pk), record in src_records.items():
            if record.model_record.pk.isdigit():
                while True:
                    new_pk = str(int(record.model_record.pk) + randint(100_000, PK_OFFSET))
                    new_key = (
                        model_label,
                        new_pk,
                    )

                    if new_key not in src_records:
                        break

                record.model_record.pk = new_pk

                replace_keys_map[(model_label, pk)] = new_key

        for old_key, new_key in replace_keys_map.items():
            src_records[new_key] = src_records.pop(old_key)

    def _transfer_src_record(
        self,
        src_record_key: str,
    ):
        """
        Перенос записи из хранилища-донора в результирующее хранилище
        """
        model_label, record_pk = src_record_key.split(
            MODEL_CLASS_NAME_ID_DELIMITER
        )

        src_record = self._src_storage.get_record(
            model_label=model_label,
            record_pk=record_pk,
        )

        src_record_get_or_create_key = (
            model_label,
            self._get_unique_preparing_model_record_key(
                record=src_record,
            ),
        )

        src_record_pk_key = (
            model_label,
            record_pk,
        )

        if src_record_get_or_create_key in self._preparing_result_model_records_map:  # noqa
            result_model_label, result_record_pk = (
                self._preparing_result_model_records_map[
                    src_record_get_or_create_key
                ]
            )

            result_record = self._result_storage.get_record(
                model_label=result_model_label,
                record_pk=result_record_pk,
            )
        else:
            result_model_record = deepcopy(src_record.model_record)

            for field_name, foreign_model_label in result_model_record.foreign_key_fields_map.items():  # noqa
                result_field_value = result_model_record.get_field_value(
                    name=field_name,
                )

                if result_field_value != 'None':
                    foreign_result_record_pk_key = (
                        foreign_model_label,
                        result_field_value.model_record.pk,
                    )

                    foreign_result_record = (
                        self._table_conformity[foreign_result_record_pk_key]
                    )

                    result_model_record.set_field_value(
                        name=field_name,
                        value=foreign_result_record,
                    )

                    foreign_result_record.has_dependence = True

            result_record = self._result_storage.add(
                model_record=result_model_record,
                tag=PreparingModelRecordTagEnum.CREATING,
                is_add_recursively_fks=True,
            )

        result_record.has_dependence = src_record.has_dependence

        self._table_conformity[src_record_pk_key] = result_record

    def _union(self):
        """
        Объединение записей хранилищ в одно общее хранилище
        """
        sorted_src_record_keys = self._sort_records(
            records=self._src_storage.records.values(),
        )

        for src_record_key in sorted_src_record_keys:
            self._transfer_src_record(
                src_record_key=src_record_key,
            )

    def run(self) -> PreparingModelRecordStorage:
        """
        Запуск действия на объединение записей хранилищ в единое хранилище
        """
        self._recalculate_src_storage_record_pks()
        self._prepare_result_storage()
        self._prepare_preparing_result_model_records_map()
        self._union()

        return self._result_storage
