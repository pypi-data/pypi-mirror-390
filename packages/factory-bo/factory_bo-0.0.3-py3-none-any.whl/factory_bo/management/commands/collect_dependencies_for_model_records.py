from typing import (
    List,
    Set,
    Tuple,
)

from django.core.management import (
    BaseCommand,
)

from factory_bo.enums import (
    PreparingModelRecordTagEnum,
)
from factory_bo.exporters import (
    HierarchyForRecordsPyFactoryExporter,
)
from factory_bo.records import (
    PreparingModelRecord,
)
from factory_bo.storages import (
    DefaultDBPreparingModelRecordStorageCreator,
    ExistingFactoryStorage,
    ModelFactoryCorrelationStorageCreator,
    PreparingModelRecordStorage,
)


class Command(BaseCommand):
    """
    Формирует иерархию фабрик для переданных записей моделей и выводит в консоль.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-label-with-id',
            action='store',
            dest='model_label_with_id',
            required=True,
            help='List of django models with id. For example: repos.DocumentTypes__1234.',
        )
        parser.add_argument(
            '--with-imports',
            action='store_true',
            dest='with_imports',
            default=False,
            help='Include python imports for factories in output.'
        )

    def _parse_model_label_with_id(
        self,
        options: dict,
    ) -> List[Tuple[str, str]]:
        """Возвращает список кортежей, содержащих пары значений - Наименование модели, Идентификатор."""

        return [tuple(record.split('__')) for record in options['model_label_with_id'].split(',')]

    def _get_preparing_model_records(
        self,
        storage: PreparingModelRecordStorage,
        model_label_with_id: List[Tuple[str, str]],
    ) -> List[PreparingModelRecord]:
        """Получает список обработанных записей моделей из хранилища.

        Args:
            storage: Хранилище обрабатываемых записей моделей.
            model_label_with_id: Список кортежей, содержащих пары значений - Наименование модели, Идентификатор.

        Returns:
            Список обработанных записей моделей.

        """
        result = []

        for model_label, record_id in model_label_with_id:
            try:
                preparing_model_record = storage.get_record(model_label, record_id)
            except KeyError as e:
                print(f'Для модели "{model_label}" не найдено записи с id "{record_id}"')

                raise e

            result.append(preparing_model_record)

        return result

    def handle(self, *args, **options):
        model_label_with_id = self._parse_model_label_with_id(options)
        with_imports = options['with_imports']

        existing_factory_storage = ExistingFactoryStorage(
            raise_on_nonexistent=False,
        )

        model_record_storage_creator = DefaultDBPreparingModelRecordStorageCreator(
            existing_factory_storage=existing_factory_storage,
        )
        preparing_model_record_storage = model_record_storage_creator.create(
            need_substitute_fk_ids=True,
            preparing_model_record_tag=PreparingModelRecordTagEnum.GETTING,
        )

        initial_preparing_model_records = self._get_preparing_model_records(
            preparing_model_record_storage,
            model_label_with_id,
        )

        preparing_model_records: Set[PreparingModelRecord] = set()
        for record in initial_preparing_model_records:
            dependencies = preparing_model_record_storage.get_dependencies_for_record_by_fk_recursively(record)
            preparing_model_records.update(dependencies)

        preparing_model_records.update(initial_preparing_model_records)

        model_factory_correlation_storage = ModelFactoryCorrelationStorageCreator(
            existing_factory_storage=existing_factory_storage,
        ).create()

        exporter = HierarchyForRecordsPyFactoryExporter(
            model_factory_correlation_storage=model_factory_correlation_storage,
            preparing_model_record_storage=preparing_model_record_storage,
            existing_factory_storage=existing_factory_storage,
        )
        result_string = exporter.to_string(preparing_model_records, with_imports)

        print(f'Для записей {model_label_with_id} сформирована иерархия фабрик:\n\n{result_string}')
