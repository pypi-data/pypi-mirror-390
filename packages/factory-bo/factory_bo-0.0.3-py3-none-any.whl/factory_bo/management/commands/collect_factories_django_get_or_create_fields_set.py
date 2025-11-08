import fileinput
import inspect
import re
from copy import (
    deepcopy,
)
from importlib import (
    import_module,
)

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)
from django.db import (
    models,
)
from django.db.models import (
    Count,
)

from factory_bo.consts import (
    GENERATED_PREFIX,
    TAB_STR,
)
from factory_bo.storages import (
    ExistingFactoryStorage,
)


class Command(BaseCommand):
    """
    Команда проверки набора полей django_get_or_create у фабрик
    на уникальность выборки, и замены набора полей на те,
    которые дают уникальную выборку у соответствующей модели.
    """

    excluded_fields = (
        'id',
        'version',
    )
    min_records_count = 2

    def add_arguments(self, parser):
        parser.add_argument(
            '--check_generated_factories',
            action='store_true',
            dest='check_generated_factories',
            default=False,
            help='Check only factories with Generated-prefix',
        )
        parser.add_argument(
            '--update_get_or_create_fields',
            action='store_true',
            dest='update_get_or_create_fields',
            default=False,
            help='Update factories django_get_or_create fields',
        )
        parser.add_argument(
            '--remove_generated_prefix',
            action='store_true',
            dest='remove_generated_prefix',
            default=False,
            help='Remove factory name Generated-prefix',
        )
        parser.add_argument(
            '--another_db_settings',
            dest='another_db_settings',
            default=None,
            help=(
                'Use database-settings to route another DB. '
                'Format: NAME|USER|PASSWORD|HOST|PORT'
            ),
        )
        parser.add_argument(
            '--factories',
            dest='factories',
            default=None,
            help=(
                'Collect get_or_create fields '
                'for one or many specified factories. '
                'Format: SomeFactoryClassName|AnotherFactoryClassName'
            ),
        )
        parser.add_argument(
            '--apps_list',
            dest='apps_list',
            default=None,
            help=(
                'Collect get_or_create fields for one or many specified apps. '
                'Format: some_app_name,another_app_name'
            ),
        )

    def log(self, message):
        print(message)

    def _extend_db_settings(self, options):
        """
        Расщирение настроек БД.
        Формат строки настроек NAME|USER|PASSWORD|HOST|PORT.
        """
        another_db_settings = options.get('another_db_settings')

        if another_db_settings:
            db_settings = another_db_settings.split('|')

            default_db_settings = deepcopy(settings.DATABASES['default'])
            default_db_settings.update({
                'NAME': db_settings[0],
                'USER': db_settings[1],
                'PASSWORD': db_settings[2],
                'HOST': db_settings[3],
                'PORT': db_settings[4],
            })
            settings.DATABASES['another_db'] = default_db_settings

    def _prepare_model_factory_map(self, raise_on_nonexistent=True) -> dict:
        """Подготавливает хранилище фабрик, а так же карты моделей.

        Args:
            raise_on_nonexistent: Вызвать исключение при отсутствии дефолтной фабрики модели.

        Returns:
            Карты соответствия моделей и их дефолтных фабрик.
        """
        existing_factory_storage = ExistingFactoryStorage(raise_on_nonexistent=raise_on_nonexistent)
        self.models_map = existing_factory_storage._model_storage._models

        return existing_factory_storage.get_model_default_factory_map()

    def _get_model_allowed_fields(self, model_label):
        """
        Получение допустимых полей модели.
        """
        return {
            field
            for field in self.models_map[model_label]['allowed_fields']
            if field not in self.excluded_fields
        }

    @classmethod
    def _check_fk_key(cls, field):
        """
        Проверка что поле - внешний ключ
        """
        return (
            isinstance(field, models.IntegerField) and
            field.attname.endswith('_id')
        ) or isinstance(field, (models.ForeignKey, models.OneToOneField))

    @classmethod
    def _get_field_priority(cls, field):
        """
        Вычисление приоритета поля в зависимости от типа или названия
        """
        if cls._check_fk_key(field):
            priority = 1
        elif isinstance(field, (models.DateField, models.DateTimeField)):
            priority = 2
        elif field.attname in {'code', 'name', 'number', 'state'}:
            priority = 3
        else:
            priority = 4

        return priority

    def _prepare_get_or_create_fields(self, factory, model_allowed_fields):
        """
        Если у фабрики есть поля get_or_create - используем их,
        а в качестве остальных полей берём разницу между
        полями модели (model_allowed_fields) и полями get_or_create фабрики.

        Если у фабрики нет полей get_or_create. То начальный набор полей
        формируем по полям внешник ключей (заканчиваются на _id),
        а в качестве остальных полей берём остальные поля модели.
        """
        get_or_create_fields = set(factory.get_or_create_fields)

        model_id_fields = {
            f.attname for f in factory.factory_model._meta.fields
            if self._check_fk_key(f) and f.attname in model_allowed_fields
        }

        if get_or_create_fields:
            another_fields = model_allowed_fields.difference(get_or_create_fields)
        else:
            get_or_create_fields = model_id_fields
            another_fields = {
                f for f in model_allowed_fields
                if f not in model_id_fields
            }

        another_fields = [
            f.attname
            for f in sorted(
                factory.factory_model._meta.fields,
                key=self._get_field_priority,
            )
            if f.attname in another_fields
        ]

        if not get_or_create_fields and another_fields:
            get_or_create_fields = {another_fields.pop(0)}

        return get_or_create_fields, another_fields

    def _enough_model_records_count(self, model, db_key):
        """
        Проверка достаточного количества записей модели
        """
        enough_records = True

        try:
            if model.objects.using(db_key).count() < self.min_records_count:
                self.log(f'\tNot enough records ({db_key}).')
                enough_records = False
        except Exception as e:
            self.log(str(e))
            enough_records = False

        return enough_records

    def _get_duplicates(self, db_key, get_or_create_fields, model):
        """
        Для конкретной БД, группировка записей модели по указанному набору полей
        с подсчётом количества и последующей фильтрацией результата
        по количеству, для выявлениня дублирующихся записей.
        """
        duplicate_records = model.objects.using(db_key).values(
            *get_or_create_fields
        ).annotate(
            duplicates_count=Count(model._meta.pk.column),
        ).filter(
            duplicates_count__gt=1,
        )

        return duplicate_records

    def _get_class_name(self, line):
        """
        Предпринимает попытку вернуть наименование класса из пришедшей строки
        из файла
        """
        class_name = ''

        class_regex = re.match(r'class (\w*)\(\w*\):', line.strip())
        if class_regex:
            class_name = class_regex.group(1)

        return class_name

    def _update_factory_fields(self, factory, get_or_create_fields, has_duplicates):
        """
        Заменить или добавить набор get_or_create-полей в класс фабрики
        """
        module_object = import_module(factory.import_path)
        factory_class = getattr(module_object, factory.factory_class_name)
        class_lines = inspect.getsourcelines(factory_class)[0]
        class_str = ''.join(class_lines)
        class_matched = False

        for line in fileinput.input([factory.module_path], inplace=True):
            if factory.factory_class_name == self._get_class_name(line):
                class_matched = True
                class_lines.pop(0)

                fields = "".join([
                    f"{TAB_STR*3}'{f}',\n"
                    for f in sorted(get_or_create_fields)
                ])
                attribute = 'django_get_or_create'
                fields = f'{attribute} = (\n{fields}{TAB_STR*2})'

                if has_duplicates:
                    fields = (
                        f'# Подобранный набор полей может не обеспечивать'
                        f' уникальность выборки\n{TAB_STR*2}{fields}'
                    )

                if attribute in class_str:
                    class_str = re.sub(
                        fr'{attribute}.+\(([^)]+)\)',
                        fields,
                        class_str,
                    )

                    if f'# {attribute}' in class_str:
                        class_str = class_str.replace(
                            f'# {attribute}',
                            f'{attribute}',
                        )
                else:
                    class_str = re.sub(
                        '(model = .+\n)',
                        f'\\g<1>{TAB_STR*2}{fields}\n',
                        class_str,
                    )

                if self.remove_generated_prefix:
                    class_str = class_str.replace(
                        f'class {GENERATED_PREFIX}',
                        'class '
                    )

                print(class_str, end='')
            elif class_matched and line in class_lines:
                class_lines.pop(0)
            else:
                print(line, end='')

    def handle(self, *args, **options):
        check_generated_factories = options.get('check_generated_factories')
        update_get_or_create_fields = options.get('update_get_or_create_fields')
        self.remove_generated_prefix = options.get('remove_generated_prefix')

        if options.get('factories'):
            specified_factories = options.get('factories').split('|')
        else:
            specified_factories = None

        self._extend_db_settings(options)

        if options.get('apps_list'):
            apps_list = options.get('apps_list').split(',')
            raise_on_nonexistent = False
        else:
            raise_on_nonexistent = True

        model_default_factory_map = self._prepare_model_factory_map(raise_on_nonexistent)

        for model_label, factory in model_default_factory_map.items():
            if model_label.split('.')[0] not in apps_list:
                continue

            factory_class_name = factory.factory_class.__name__

            if (
                specified_factories and
                factory_class_name not in specified_factories
            ) or (
                check_generated_factories and
                not factory_class_name.startswith(GENERATED_PREFIX)
            ):
                # пропуск уже актуализированных фабрик
                continue

            model = factory.factory_class.get_model()
            model.objects = model._base_manager

            self.log(f'\n{factory.factory_class_name} - {model_label}')

            model_allowed_fields = self._get_model_allowed_fields(
                model_label
            )
            
            if not model_allowed_fields:
                self.log('\tModel has no "allowed_fields".')
                continue

            factory_get_or_create_fields, another_fields = self._prepare_get_or_create_fields(
                factory,
                model_allowed_fields,
            )

            if model._meta.unique_together:
                get_or_create_fields = {
                    f.attname
                    for f in model._meta.fields
                    if f.name in model._meta.unique_together[0]
                }

                has_duplicates = False
            else:
                get_or_create_fields = factory_get_or_create_fields

                db_duplicates = {}

                for db_key in settings.DATABASES:

                    if not self._enough_model_records_count(model, db_key):
                        continue

                    duplicates_exists = True
                    another_fields_exists = True

                    while duplicates_exists and another_fields_exists:
                        duplicate_records = self._get_duplicates(
                            db_key,
                            get_or_create_fields,
                            model,
                        )
                        duplicates_exists = duplicate_records.exists()

                        if duplicates_exists and another_fields:
                            get_or_create_fields.add(another_fields.pop(0))
                        elif not another_fields:
                            another_fields_exists = False

                    if duplicates_exists:
                        self.log(
                            f'\tDuplicate records found! ({db_key}) '
                            f'django_get_or_create - '
                            f'{", ".join(get_or_create_fields)}'
                        )
                        self.log(f'\t\t{duplicate_records.query}')
                    else:
                        self.log(
                            f'\tNo duplicates found! ({db_key}) '
                            f'django_get_or_create - '
                            f'{", ".join(get_or_create_fields)}'
                        )

                    db_duplicates[db_key] = duplicates_exists

                has_duplicates = any(db_duplicates.values())

            if (
                get_or_create_fields and
                    update_get_or_create_fields and
                    factory.get_or_create_fields != get_or_create_fields
            ):
                self._update_factory_fields(
                    factory,
                    get_or_create_fields,
                    has_duplicates,
                )
            elif not get_or_create_fields:
                self.log('\tDjango_get_or_create-fields was not collected.')
