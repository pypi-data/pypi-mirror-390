import glob
import os
import sys
from collections import (
    defaultdict,
    namedtuple,
)
from contextlib import (
    contextmanager,
)
from itertools import (
    chain,
    islice,
)
from typing import (
    Any,
    Dict,
    Iterable,
)

from django.conf import (
    settings,
)
from django.db import (
    close_old_connections,
    connections,
)
from django.db.utils import (
    load_backend,
)

from factory_bo.consts import (
    TAB_STR,
)


Results = namedtuple('Results', ['sorted', 'cyclic'])


@contextmanager
def substitute_default_db_connection(
    db_connection_settings: Dict[str, Any],
):
    """
    Менеджер контекста предназначен для подмены дефолтного подключения БД на
    пользовательский на время выполения сценария
    """
    temp_db_connection = connections['default']
    temp_db_connection_settings = temp_db_connection.settings_dict.copy()
    try:
        close_old_connections()
        backend = load_backend(db_connection_settings['ENGINE'])
        db_connection = backend.DatabaseWrapper(
            db_connection_settings,
            alias='default',
        )
        db_connection.connect()
        connections['default'] = db_connection

        yield

    except Exception as e:
        print(e)
    finally:
        close_old_connections()

        backend = load_backend(temp_db_connection_settings['ENGINE'])
        connections['default'] = backend.DatabaseWrapper(
            temp_db_connection_settings,
            alias='default',
        )
        connections['default'].connect()


@contextmanager
def substitute_model_get_queryset_method(model):
    """
    Контекстный менеджер подмены метода get_queryset
    стандартного менеджера модели objects, на метод базового менеджера.

    Подмена нужна для случаев когда менеджер модели по-умолчанию дополнительно фильтрует QS.
    В частности чтобы исключить фильтрацию по end_id у моделей наследованных
    от BaseModelWithEnterprise (менеджер EnterpriseDictionaryRecordManager).
    """
    try:
        has_get_queryset_back = hasattr(
            model.objects,
            '_get_queryset_back'
        )
    except RecursionError:
        # Вход в рекурсию происходит из-за метода
        # salary.core.base.models.PassThroughManagerMixin.__getattr__
        # который при попытке получить несуществующий атрибут
        # начинает рекурсивно вызывать сам себя
        # TODO BOZIK-28931
        has_get_queryset_back = False

    if not has_get_queryset_back:
        model.objects._get_queryset_back = model.objects.get_queryset

    model.objects.get_queryset = model._base_manager.get_queryset

    try:
        yield
    finally:
        model.objects.get_queryset = model.objects._get_queryset_back


class FactoryRepr(object):
    """
    Представление записи фабрики в виде строки
    """
    def __init__(
        self,
        factory_class_name: str,
        fields: Dict[str, str],
        is_formatted: bool = False,
        start_indent: str = '',
    ):
        self._factory_class_name = factory_class_name
        self._fields = fields
        self._is_formatted = is_formatted
        self._start_indent = start_indent

    def as_dict(self):
        return f'{self._factory_class_name}(**{self._fields})'

    def as_str(self):
        field_indent = (
            f'{self._start_indent}{TAB_STR}' if
            self._is_formatted else
            ''
        )
        fields_values = [
            f'{field_indent}{x}={y}'
            for x, y in self._fields.items()
        ]

        if self._is_formatted:
            fields_values_str = ',\n'.join(fields_values)
            if fields_values_str:
                fields_values_str = f'{fields_values_str},'

            repr_ = (
                f'{self._factory_class_name}(\n'
                f'{fields_values_str}\n{TAB_STR})'
            )
        else:
            fields_values_str = ', '.join(fields_values)
            repr_ = f'{self._factory_class_name}({fields_values_str})'

        return repr_


def is_pseudo_fk_field(
    field_name: str,
) -> bool:
    """
    Является ли поле псевдо внешним ключом
    """
    return (
        field_name in settings.FACTORY_BO__PSEUDO_SELF_FK_IDS or
        field_name in settings.FACTORY_BO__PSEUDO_FK_IDS
    )


def make_chunks(
    iterable: Iterable,
    size: int,
    is_list: bool = False,
):
    """
    Эффективный метод нарезки итерабельного объекта на куски
    """
    iterator = iter(iterable)

    for first in iterator:
        yield (
            list(chain([first], islice(iterator, size - 1))) if
            is_list else
            chain([first], islice(iterator, size - 1))
        )


def get_pk_slug(
    pk: str,
):
    """
    Метод преобразования первичного ключа к виду для использования, как части
    названия переменной
    """
    return pk.replace('\'', '').replace('-', '_')


def colored_stdout_output(
    message: str,
    color: int,
):
    """
    Вывод сообщения в основной поток вывода с форматированием цветом

    :param message: сообщение
    :param color: код цвета
    :return:
    """
    new_message = f'\33[{color};1m{message}\33[0m\n'

    sys.stdout.write(new_message)


def get_last_edited_fixtures():
    """
    Получение абсолютных путей последних отредактированных фикстур
    """
    fixtures_dir_path = settings.FACTORY_BO__FIXTURES_DIR_PATH

    fixtures = glob.glob(os.path.join(fixtures_dir_path, '*.json'))
    sorted_fixtures = sorted(
        fixtures,
        key=os.path.getctime,
        reverse=True,
    )

    return sorted_fixtures[1], sorted_fixtures[0]


def check_fixture_files(
    begin_file_name: str,
    end_file_name: str,
):
    """
    Проверка существования файлов. Возвращает полные пути файлов фикстур
    до и после выполнения действий предыстории
    """
    if not begin_file_name:
        raise SystemExit('Check begin_file_name parameter')

    if not end_file_name:
        raise SystemExit('Check end_file_name parameter')

    fixtures_dir_path = settings.FACTORY_BO__FIXTURES_DIR_PATH

    begin_file_path = os.path.join(fixtures_dir_path, begin_file_name)
    if not os.path.exists(begin_file_path):
        raise SystemExit('Begin file does not exists')

    end_file_path = os.path.join(fixtures_dir_path, end_file_name)
    if not os.path.exists(end_file_path):
        raise SystemExit('End file does not exists')

    return begin_file_path, end_file_path


def topological_sort(dependency_pairs):
    """
    Топологическая сортировка графов. На вход подаются ребра графа в виде
    кортежей названий вершин.

    Алгоритм отлично подходит для сортировки порядка следования таблиц
    относительно зависимостей между ними.

    django.utils.topological_sort.stable_topological_sort - работает только с
    одним графом, тут можно подать несколько графов на вход

    print( topological_sort('aa'.split()) )
    print( topological_sort('ah bg cf ch di ed fb fg hd he ib'.split()) )

    Данный код является заимствованным из открытых источников.
    Спасибо Raymond Hettinger
    """
    num_heads = defaultdict(int)
    tails = defaultdict(list)
    heads = []
    for h, t in dependency_pairs:
        num_heads[t] += 1
        if h in tails:
            tails[h].append(t)
        else:
            tails[h] = [t]
            heads.append(h)

    ordered = [h for h in heads if h not in num_heads]
    for h in ordered:
        for t in tails[h]:
            num_heads[t] -= 1
            if not num_heads[t]:
                ordered.append(t)
    cyclic = [n for n, heads in num_heads.items() if heads]

    return Results(ordered, cyclic)
