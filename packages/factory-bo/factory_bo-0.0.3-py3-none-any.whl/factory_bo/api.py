import codecs
import datetime
import os
import sys
from typing import (
    Optional,
)

from django.conf import (
    settings,
)

from factory_bo.enums import (
    DiffFormatEnum,
    FixtureDestinationEnum,
)
from factory_bo.exporters import (
    JSONModelExporter,
    PyFactoryExporter,
)
from factory_bo.helpers import (
    check_fixture_files,
    get_last_edited_fixtures,
)
from factory_bo.storages import (
    DefaultDBPreparingModelRecordStorageCreator,
    ExistingFactoryStorage,
    JSONPreparingModelStorageCreator,
    ModelFactoryCorrelationStorageCreator,
    PreparingModelRecordStorage,
)
from factory_bo.strings import (
    FACTORY_BO__FIXTURES_DIR_PATH_NOT_FOUND,
    WRONG_DIFF_FORMAT,
    WRONG_FIXTURE_FILE_EXTENSION_ERROR,
)


def get_preparing_model_record_storage_from_file(
    file_path: str,
    existing_factory_storage: ExistingFactoryStorage,
    fk_source_storage: Optional[PreparingModelRecordStorage] = None,
) -> PreparingModelRecordStorage:
    """
    Получение хранилища кешей фабрик на основе контента фикстур фабрик
    """
    with open(file_path, 'r') as f:
        factories_json = f.read()

    factory_cache_storage_creator = JSONPreparingModelStorageCreator(
        factories_json=factories_json,
        existing_factory_storage=existing_factory_storage,
    )

    return factory_cache_storage_creator.create(
        need_substitute_fk_ids=True,
        fk_source_storage=fk_source_storage,
    )


def create_models_json_fixture(
    fixture_destination: str = FixtureDestinationEnum.FILE,
    fixture_file_path: str = '',
):
    """
    Функция создания фикстуры записей моделей.

    Фикстура представлена в виде JSON-файла, содержащего в качестве ключа
    <app_name>.<model_class_name> и в качестве значения списка параметров для
    создания записей моделей.

    Вывод может осуществляться в стандартный поток вывода, либо в файл. За это
    поведение отвечает параметр fixture_destination. Принимает значения stdout
    или file.

    Если заранее известен абсолютный путь результирующего файла для выгрузки,
    то его можно указать с помощью параметра fixture_file_path. Аргумент
    должен заканчиваться на ".json". Если путь заранее не известен, то выгрузка
    будет произведена в файл FIXTURES_DIR_PATH.fixture_{%Y%m%d_%H%M%S}.json
    """
    if fixture_destination == FixtureDestinationEnum.FILE:
        if fixture_file_path:
            if fixture_file_path.endswith('.json'):
                file_path = fixture_file_path
            else:
                raise OSError(
                    WRONG_FIXTURE_FILE_EXTENSION_ERROR
                )
        else:
            now = datetime.datetime.now()
            file_path = os.path.join(
                settings.FACTORY_BO__FIXTURES_DIR_PATH,
                f'fixture_{now.strftime("%Y%m%d_%H%M%S")}.json'
            )

        dir_path = os.path.split(file_path)[0]

        os.makedirs(
            dir_path,
            exist_ok=True
        )
        f = codecs.open(file_path, 'w', encoding='utf-8')
    else:
        f = sys.stdout

    existing_factory_storage = ExistingFactoryStorage()

    preparing_model_storage_creator = (
        DefaultDBPreparingModelRecordStorageCreator(
            existing_factory_storage=existing_factory_storage,
        )
    )

    preparing_model_record_storage = (
        preparing_model_storage_creator.create()
    )

    json_model_exporter = JSONModelExporter(
        preparing_model_record_storage=preparing_model_record_storage,
        existing_factory_storage=existing_factory_storage,
    )

    content = json_model_exporter.to_string()

    f.write(content)
    f.close()


def create_diff_factories_fixture(
    begin_file_name: Optional[str] = None,
    end_file_name: Optional[str] = None,
    diff_format: str = DiffFormatEnum.PYTHON,
    result_file_path: Optional[str] = None,
):
    """
    Функция предназначена для получения предыстории тестов. Перед выполнением
    действий необходимо снять дамп эталонной базы в виде фикстуры с помощью
    команды make_factories_fixtures. После чего выполняются действия
    предыстории. Далее снимается второй дамп базы данных в виде фикстур.

    После чего выполняется данная функция, которая позволяет получить разницу
    между файлами с отсортированными фабриками и расставленными переменными
    вместо идентификаторов.

    Идентификаторы частично остаются из-за того, что объекты, на которые идет
    ссылка не создавались во время выполнения действий предыстории.

    Важно! В секции factory_bo конфигурационного файла нужно указать
    FIXTURES_DIR_PATH - абсолютный путь до директории, в которой
    хранятся фикстуры для тестирования. Начальная и конечная фиктуры должны
    быть созданы либо перенесены в данную директорию.

    Для работы функции могут быть указаны наименования фикстуры с фабриками
    полученные до и после выполнения действий предыстории с помощью параметров
    begin_factories_fixture_name и end_factories_fixture_name. Если эти
    параметры не будут указаны или будут заданы частично, то будет произведен
    поиск последних отредатированных фикстур фабрик и разница будет находиться
    между ними. Валидными являются фикстуры с контентом в формате JSON.

    Выгрузка может производиться в виде Python с полностью подготовленным кодом
    фикстуры фабрик для исполнения. Также есть возможность выгузки в виде
    SQL-запросов, полученных после исполнения Python-кода, полученного на
    предыщем шаге. Формат выгрузки можно указать с помощью параметра
    diff_format, который может принимать значение py или sql (выгрузка в
    формате SQL в данный момент не поддерживается).

    Если заранее известен абсолюный путь резульрирующего файла, то его можно
    указать с помощью параметра result_file_path. Данный параметр является не
    обязательным. Если он не указан, то выгрузка будет произведена в файл
    FIXTURES_DIR_PATH/diff_result/diff_fixtures__{%Y_%m_%d__%H_%M_%S}.{diff_format}.
    """
    if not settings.FACTORY_BO__FIXTURES_DIR_PATH:
        raise SystemExit(
            FACTORY_BO__FIXTURES_DIR_PATH_NOT_FOUND
        )

    if diff_format not in DiffFormatEnum.values:
        raise ValueError(
            WRONG_DIFF_FORMAT.format(str(diff_format))
        )

    if not begin_file_name or not end_file_name:
        begin_file_path, end_file_path = get_last_edited_fixtures()
    else:
        begin_file_path, end_file_path = check_fixture_files(
            begin_file_name=begin_file_name,
            end_file_name=end_file_name,
        )

    existing_factory_storage = ExistingFactoryStorage()

    begin_preparing_model_record_storage = (
        get_preparing_model_record_storage_from_file(
            file_path=begin_file_path,
            existing_factory_storage=existing_factory_storage,
        )
    )
    end_preparing_model_record_storage = (
        get_preparing_model_record_storage_from_file(
            file_path=end_file_path,
            fk_source_storage=begin_preparing_model_record_storage,
            existing_factory_storage=existing_factory_storage,
        )
    )

    difference_storage = end_preparing_model_record_storage.difference(
        begin_preparing_model_record_storage
    )

    correlation_storage_creator = ModelFactoryCorrelationStorageCreator(
        existing_factory_storage=existing_factory_storage,
    )

    correlation_storage = correlation_storage_creator.create()

    py_factory_exporter = PyFactoryExporter(
        preparing_model_record_storage=difference_storage,
        model_factory_correlation_storage=correlation_storage,
        existing_factory_storage=existing_factory_storage,
    )

    result_file_path = py_factory_exporter.to_file(
        file_path=result_file_path,
    )

    return result_file_path
