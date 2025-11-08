from django.core.management import (
    BaseCommand,
)

from factory_bo.api import (
    create_diff_factories_fixture,
)
from factory_bo.enums import (
    DiffFormatEnum,
)


class Command(BaseCommand):
    """
    Команда предназначена для получения предыстории тестов. Перед выполнением
    действий необходимо снять дамп эталонной базы в виде фикстуры с помощью
    команды make_factories_fixtures. После чего выполняются действия
    предыстории. Далее снимается второй дамп базы данных в виде фикстур.

    После чего выполняется данная команда, которая позволяет получить разницу
    между файлами с отсортированными фабриками и расставленными переменными
    вместо идентификаторов.

    Идентификаторы частично остаются из-за того, что объекты, на которые идет
    ссылка не создавались во время выполнения действий предыстории.

    Важно! В секции factory_bo конфигурационного файла нужно указать
    FIXTURES_DIR_PATH - абсолютный путь до директории, в которой
    хранятся фикстуры для тестирования. Начальная и конечная фиктуры должны
    быть созданы либо перенесены в данную директорию.

    Для работы команды могут быть указаны наименования фикстуры с фабриками
    полученные до и после выполнения действий предыстории с помощью параметров
    --begin_factories_fixture_name и --end_factories_fixture_name. Если эти
    параметры не будут указаны или будут заданы частично, то будет произведен
    поиск последних отредатированных фикстур фабрик и разница будет находиться
    между ними. Валидными являются фикстуры с контентом в формате JSON.

    Выгрузка может производиться в виде Python с полностью подготовленным кодом
    фикстуры фабрик для исполнения. Также есть возможность выгузки в виде
    SQL-запросов, полученных после исполнения Python-кода, полученного на
    предыщем шаге. Формат выгрузки можно указать с помощью параметра
    --diff_format, который может принимать значение py или sql.

    Если заранее известен абсолюный путь резульрирующего файла, то его можно
    указать с помощью параметра --result_file_path. Данный параметр является не
    обязательным. Если он не указан, то выгрузка будет произведена в файл
    FIXTURES_DIR_PATH/diff_result/diff_fixtures__{%Y_%m_%d__%H_%M_%S}.{diff_format}.

    Пример запуска:
    python manage.py make_diff_fixtures --begin_factories_fixture_name begin.py --end_factories_fixture_name end.py  --diff_format=py --result_file_path=/some_path/some_file.py
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--begin_factories_fixture_name',
            action='store',
            dest='begin_factories_fixture_name',
            help='Factories fixture name before actions',
        )

        parser.add_argument(
            '--end_factories_fixture_name',
            action='store',
            dest='end_factories_fixture_name',
            help='Factories fixture name after actions',
        )

        parser.add_argument(
            '--diff_format',
            action='store',
            dest='diff_format',
            default=DiffFormatEnum.PYTHON,
            help=(
                'Diff export format. You can choose py or sql format. '
                'Default is py.'
            ),
        )

        parser.add_argument(
            '--result_file_path',
            action='store',
            dest='result_file_path',
            default=None,
            help=(
                'File path for exporting results.'
            ),
        )

    def handle(self, *args, **options):
        begin_file_name = options.get('begin_factories_fixture_name')
        end_file_name = options.get('end_factories_fixture_name')
        diff_format = options.get('diff_format')
        result_file_path = options.get('result_file_path')

        result_file_path = create_diff_factories_fixture(
            begin_file_name=begin_file_name,
            end_file_name=end_file_name,
            diff_format=diff_format,
            result_file_path=result_file_path,
        )

        self.stdout.write(
            f'Difference fixtures result file path - {result_file_path}'
        )
