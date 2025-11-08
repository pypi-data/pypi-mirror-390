from django.core.management import (
    BaseCommand,
)

from factory_bo.api import (
    create_models_json_fixture,
)
from factory_bo.enums import (
    FixtureDestinationEnum,
)


class Command(BaseCommand):
    """
    Команда создания фикстуры записей моделей.

    Фикстура представлена в виде JSON-файла, содержащего в качестве ключа
    <app_name>.<model_class_name> и в качестве значения списка параметров для
    создания записей моделей.

    Вывод может осуществляться в стандартный поток вывода, либо в файл. За это
    поведение отвечает параметр --fixture_destination. Принимает значения stdout
    или file.

    Если заранее известен абсолютный путь результирующего файла для выгрузки,
    то его можно указать с помощью параметра --fixture_file_path. Аргумент
    должен заканчиваться на ".json". Если путь заранее не известен, то выгрузка
    будет произведена в файл FIXTURES_DIR_PATH.fixture_{%Y%m%d_%H%M%S}.json
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture_destination',
            action='store',
            dest='fixture_destination',
            default=FixtureDestinationEnum.FILE,
            help=(
                'Output method. You can choose stdout or file. Default is '
                'stdout.'
            )
        )

        parser.add_argument(
            '--fixture_file_path',
            action='store',
            dest='fixture_file_path',
            help=(
                'Absolute path of fixture json file.'
            )
        )

    def handle(self, *args, **options):
        fixture_destination = options['fixture_destination']
        fixture_file_path = options['fixture_file_path'] or ''

        create_models_json_fixture(
            fixture_destination=fixture_destination,
            fixture_file_path=fixture_file_path,
        )
