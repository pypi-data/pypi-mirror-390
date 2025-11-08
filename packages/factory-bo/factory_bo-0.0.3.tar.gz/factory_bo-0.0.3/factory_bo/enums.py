from typing import (
    Set,
)


class PreparingModelRecordTagEnum:
    GETTING = 1
    CREATING = 2
    UPDATING = 3
    DELETING = 4

    values = {
        GETTING: 'Получаемая запись',
        CREATING: 'Создаваемая запись',
        UPDATING: 'Обновляемая запись',
        DELETING: 'Удаляемая запись',
    }

    ALL = (
        GETTING,
        CREATING,
        UPDATING,
        DELETING,
    )

    # Несовместимые состояния записи модели
    INCOMPATIBLES = (
        CREATING,
        UPDATING,
        DELETING,
    )

    @classmethod
    def is_incompatible(
        cls,
        tag: int,
    ):
        """
        Относится к несовместимым
        """
        return tag in cls.INCOMPATIBLES

    @classmethod
    def have_incompatible(
        cls,
        tags: Set[int],
    ):
        """
        Показывает, что набор тегов уже содержит несовместимые состояния записи
        модели
        """
        return bool(tags.intersection(cls.INCOMPATIBLES))

    @classmethod
    def is_updating(
        cls,
        tag: int,
    ):
        """
        Является обновляемым
        """
        return tag == cls.UPDATING

    @classmethod
    def is_deleting(
        cls,
        tag: int,
    ):
        """
        Является удаляемым
        """
        return tag == cls.DELETING


class DiffFormatEnum:
    PYTHON = 'py'
    SQL = 'sql'

    values = {
        PYTHON: 'Выгрузка в виде Python-файла содержащего фабрики',
        SQL: (
            'Выгрузка в виде SQL-файла с запросами сгенерированными после '
            'исполнения кода из Python-файла с фабриками'
        ),
    }


class UsingLibraryEnum:
    DATETIME = 'datetime'
    DECIMAL = 'Decimal'
    JSON = 'json.'

    values = {
        DATETIME: 'import datetime',
        DECIMAL: 'from decimal import Decimal',
        JSON: 'import json',
    }


class FixtureDestinationEnum:
    STDOUT = 'stdout'
    FILE = 'file'

    values = {
        STDOUT: 'Вывод производится в стандартный поток вывода',
        FILE: 'Вывод производится в файл',
    }


class EtalonFixtureGeneratorModeEnum:
    MERGE = 'merge'
    REPLACE = 'replace'

    values = {
        MERGE: (
            'Режим объединения данных существующих фикстур с данными уже '
            'существующих'
        ),
        REPLACE: 'Режим замены без учета уже существующих данных',
    }


class FactoryUseTypeEnum:
    DEFAULT = 1
    CUSTOM = 2

    values = {
        DEFAULT: 'Фабрика используется по умолчанию',
        CUSTOM: (
            'Фабрику нужно явно указать в словаре соответствия model_name, '
            'factory_class_name декоратора теста'
        ),
    }

    @classmethod
    def is_default(
        cls,
        type_: int,
    ):
        """
        Фабрика является дефолтной для модели
        """
        return type_ == cls.DEFAULT

    @classmethod
    def is_custom(
        cls,
        type_: int,
    ):
        """
        Фабрика является кастомной для модели
        """
        return type_ == cls.CUSTOM

    @classmethod
    def exists(
        cls,
        use_type: int
    ):
        """
        Проверяется существование типа использования
        """
        return use_type in cls.values.keys()
