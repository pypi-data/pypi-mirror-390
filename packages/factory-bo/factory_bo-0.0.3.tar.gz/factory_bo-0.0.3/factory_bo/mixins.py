import os
from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    Iterable,
    List,
    Optional,
)

from factory_bo.helpers import (
    topological_sort,
)

from factory_bo.records import (
    PreparingModelRecord,
)


class BaseExporter(metaclass=ABCMeta):
    """
    Абстрактный класс создания экспортеров
    """

    @abstractmethod
    def to_string(
        self,
        *args,
        **kwargs,
    ) -> str:
        pass

    def to_file(
        self,
        *args,
        file_path: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Вывод результата экспорта в файл
        """
        if not file_path:
            raise ValueError()

        content = self.to_string(*args, **kwargs)

        if content:
            dir_path = os.path.split(file_path)[0]

            os.makedirs(
                dir_path,
                exist_ok=True,
            )

            with open(file_path, 'w') as f:
                f.write(content)
        else:
            print(
                f'File with path "{file_path}" can not create with empty '
                f'content!'
            )

            file_path = ''

        return file_path


class PreparingModelSortMixin:
    """
    Миксин, добавляющий функциональность сортировки обрабатываемых записей по
    степени зависимости между ними
    """

    def _sort_records(
        self,
        records: Iterable[PreparingModelRecord],
        is_reversed: bool = True,
    ) -> List[str]:
        """
        Сортировка обрабатываемых записей
        """
        model_record_id_pairs = set()

        all_model_record_ids = {
            record.model_record.model_label_with_pk
            for record in records
        }

        processed_model_record_ids = set()

        for record in records:
            fk_field_names = set(record.model_record.fk_field_names)
            existing_factory = self._model_factory_correlation_storage.get_existing_factory(
                record.model_record.model_label,
            )
            excluded_fk_fields = existing_factory.excluded_fk_fields

            if excluded_fk_fields:
                fk_field_names = fk_field_names.difference(excluded_fk_fields)

            for field_name in fk_field_names:
                fk_field_value = record.model_record.fields.get(field_name)

                if (
                    fk_field_value and
                    isinstance(fk_field_value, PreparingModelRecord)
                ):
                    model_record_id = record.model_record.model_label_with_pk
                    fk_model_record_id = fk_field_value.model_record.model_label_with_pk

                    if fk_model_record_id not in all_model_record_ids:
                        # Если связанной записи нет в сортируемом изначальном наборе записей, пропускаем
                        continue

                    model_record_id_pairs.add(
                        (
                            model_record_id,
                            fk_model_record_id,
                        )
                    )

                    processed_model_record_ids.add(model_record_id)
                    processed_model_record_ids.add(fk_model_record_id)

        model_record_ids_without_relations = all_model_record_ids.difference(processed_model_record_ids)

        sorting_result = topological_sort(model_record_id_pairs)

        sorted_model_record_ids = (
            list(model_record_ids_without_relations) +
            sorting_result.cyclic +
            list(
                reversed(sorting_result.sorted) if
                is_reversed else
                sorting_result.sorted
            )
        )

        return sorted_model_record_ids
