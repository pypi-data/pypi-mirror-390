import contextlib
import json
from operator import (
    itemgetter,
)
from typing import (
    Callable,
    Tuple,
)

from django.db import (
    connection,
)
from factory import (
    DjangoModelFactory,
    FactoryError,
)
from factory.base import (
    OptionDefault,
)
from factory.django import (
    DjangoOptions,
)

from factory_bo.enums import (
    FactoryUseTypeEnum,
)


class WebBBOptions(DjangoOptions):
    def _build_default_options(self):
        """
        Добавление новых полей, которые валидны для указания в class Meta фабрик
        """
        options = super()._build_default_options()
        options.extend([
            OptionDefault('auto_updated_fields', ()),
            OptionDefault('allow_use_id_field', False),
            OptionDefault('excluded_fk_fields', ()),
        ])

        return options


class WebBBModelFactory(DjangoModelFactory):
    """
    Переопределенный базовый класс фабрики проекта web_bb
    """
    # Указывает вид использования фабрики. У каждой модели должна быть одна
    # соответствующая дефолтная фабрики и неограниченное количество кастомных,
    # которые могут быть использованы по-необходимости в тестах
    _factory_use_type = FactoryUseTypeEnum.DEFAULT

    # Режим проверки наличия записи модели.
    # По-умолчанию инстанцирование класса фабрики выполняет получение записи из БД, и в случае отсутствия записи
    # вызывается исключение. При отключенной проверке в случае отсутствия записи в БД, выполняется
    # стандартная логика создания записи из get_or_create.
    _check_record_existence = True

    _options_class = WebBBOptions

    @classmethod
    def get_django_get_or_create(cls) -> Tuple[str]:
        """
        Возвращает набор полей django_get_or_create фабрики
        """
        return getattr(
            cls._meta,
            'django_get_or_create',
            ()
        )

    @classmethod
    def get_django_get_or_create_getter(cls) -> Callable:
        """
        Возвращает itemgetter набора полей django_get_or_create фабрики
        """
        django_get_or_create = cls.get_django_get_or_create()

        return itemgetter(*django_get_or_create)

    @classmethod
    def get_factory_use_type(cls):
        """
        Возвращает тип использования фабрики
        """
        return cls._factory_use_type

    @classmethod
    def get_model(cls):
        return cls._meta.model

    @classmethod
    def get_model_label(cls):
        """
        Возвращает лейбел модели фабрики
        """
        return cls._meta.model._meta.label

    @classmethod
    def get_auto_updated_fields(cls):
        """
        Возвращает поля с автогенерируемыми значениями для фабрики
        """
        return getattr(cls._meta, 'auto_updated_fields', ())

    @classmethod
    def get_allow_use_id_field(cls):
        """
        Возвращает признак возможности использования поля ID для выборки
        и создания объектов при инстанцировании фабрик
        """
        return getattr(cls._meta, 'allow_use_id_field', False)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        super()._after_postgeneration(instance, create, results)

        if cls._meta.allow_use_id_field:
            cls.increase_pk_sequence_value(
                instance._meta.db_table,
                instance._meta.pk.column,
            )

    @staticmethod
    def increase_pk_sequence_value(db_table, pk_column):
        """
        Сдвиг последовательности ID таблицы вперёд
        """
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT setval(
                    pg_get_serial_sequence('{db_table}', '{pk_column}'),
                    max({pk_column})
                ) FROM "{db_table}";
            """)

    @classmethod
    def get_excluded_fk_fields(cls):
        """
        Возвращает набор полей внешних ключей для исключения при
        простановке зависимостей
        """
        return getattr(cls._meta, 'excluded_fk_fields', ())

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        """Create an instance of the model through objects.get_or_create."""
        cls.check_record_existence(args, kwargs, model_class)
        return super()._get_or_create(model_class, *args, **kwargs)

    @classmethod
    def check_record_existence(cls, args, kwargs, model_class):
        """Проверка наличия записи модели по указанным параметрам."""
        if '_check_exists' in kwargs:
            arg_check_exists = kwargs.pop('_check_exists')
        else:
            arg_check_exists = True

        manager = cls._get_manager(model_class)
        key_fields = {}

        for field in cls._meta.django_get_or_create:
            if field not in kwargs:
                raise FactoryError(
                    f"django_get_or_create - "
                    f"Unable to find initialization value for '{field}' in factory {cls.__name__}"
                )
            key_fields[field] = kwargs[field]

        is_instance_exists = manager.filter(*args, **key_fields).exists()

        if (cls._check_record_existence and arg_check_exists) and not is_instance_exists:
            str_kwargs = '\n\t\t'.join([f'{k}: {v}' for k, v in kwargs.items()])

            # Создание qs'та с фильтрацией по совпадающим полям, сохранение наименований отличающихся.
            not_matching_fields = []
            qs = manager.values(*key_fields)
            for field_with_value in key_fields.items():
                if qs.filter(field_with_value).exists():
                    qs = qs.filter(field_with_value)
                else:
                    not_matching_fields.append(field_with_value[0])

            partially_matching_records = json.dumps(list(qs), default=str, indent=True, ensure_ascii=False)
            raise Exception(
                f'Не найдена запись модели "{model_class.__name__}"!\n'
                f'Параметры фильтрации:\nargs: {args}\nkwargs:\n\t\t{str_kwargs}\n\n'
                f'Записи, отличающиеся значением поля/ей "{", ".join(not_matching_fields)}":\n'
                f'{partially_matching_records}'
            )

    @classmethod
    @contextlib.contextmanager
    def disable_check_existence(cls):
        """Контекстный менеджер отключения проверки наличия записи модели."""
        cls._check_record_existence = False
        yield
        cls._check_record_existence = True


class DefaultManagerFactory(WebBBModelFactory):
    """
    Базовый класс фабрик с переопределенным менеджером
    """

    @classmethod
    def _get_manager(cls, model_class):
        manager = model_class._base_manager

        return manager

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        old_provider_use = getattr(model_class, 'provider_use', None)

        model_class.provider_use = True

        manager = cls._get_manager(model_class)

        if cls._meta.django_get_or_create:
            obj = cls._get_or_create(model_class, *args, **kwargs)
        else:
            obj = manager.create(*args, **kwargs)

        if old_provider_use:
            model_class.provider_use = old_provider_use
        else:
            del model_class.provider_use

        return obj
