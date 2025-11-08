from copy import (
    copy,
    deepcopy,
)
from typing import (
    Any,
    Dict,
    Optional,
    Set,
    Type,
)

from django.apps import (
    apps,
)
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    Model,
)

from factory_bo.consts import (
    MODEL_CLASS_NAME_ID_DELIMITER,
)
from factory_bo.enums import (
    PreparingModelRecordTagEnum,
)
from factory_bo.signals import (
    prepare_record_foreign_key_fields_map_signal,
)


class ModelRecord:
    """
    Запись модели
    """

    def __init__(
        self,
        model_class: Type[Model],
        foreign_key_fields_map: Dict[str, str],
        fields: Dict[str, Any],
        content_type_cache: Dict[int, ContentType],
    ):
        self._model_class: Type[Model] = model_class
        self._fields = fields

        # Если есть поле id, то проставляется значение из него и удаляется из
        # списка полей, если нет, то присваивается значение первичного ключа
        # модели. Первичным ключом может выступать внешний ключ и тогда поле
        # не нужно убирать из списка полей.
        pk = self._model_class._meta.pk
        self._pk = (
            self._fields[pk.attname] if (
                pk.is_relation or
                # подразумевается, что может прилететь UUID в виде строки
                not self._fields[pk.attname].isdigit()
            ) else
            self._fields.pop(pk.attname, None)
        )

        # На случай, если какое-то поле кроме id является первичным ключом
        if 'id' in self._fields.keys():
            self._fields.pop('id')

        # Копируем foreing_key_field_map для дальнейшего расширения
        # GeneficForegnKey и прочих
        self._foreign_key_fields_map: Dict[str, str] = deepcopy(
            foreign_key_fields_map
        )

        self._prepare_foreign_key_fields_map(content_type_cache)

        self._fk_field_names = self._prepare_fk_field_names()

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} '
            f'@model_label="{self.model_label}" '
            f'@pk={self._pk}>'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def pk(self):
        return self._pk

    @pk.setter
    def pk(
        self,
        value,
    ):
        self._pk = str(value)

    @property
    def all_fields(self) -> Dict[str, str]:
        """
        Возвращает все поля фабрики в виде словаря
        """
        fields = copy(self.fields)
        fields[self._model_class._meta.pk.attname] = (
            self._pk
        )

        return fields

    @property
    def fields(self) -> Dict[str, str]:
        return self._fields

    @property
    def model_label(self) -> str:
        return self._model_class._meta.label

    @property
    def model_class(self) -> Type[Model]:
        return self._model_class

    @property
    def key(self) -> tuple:
        return (
            self.model_label,
            self.pk,
        )

    @property
    def foreign_key_fields_map(self) -> Dict[str, str]:
        return self._foreign_key_fields_map

    @property
    def fk_field_names(self):
        """
        Возвращает исчерпывающий список имен полей внешних ключей
        """
        return self._fk_field_names

    @property
    def model_label_with_pk(self):
        """
        Возвращает строку с названием модели и id записи разделённые специальным разделителем.
        """
        return f'{self.model_label}{MODEL_CLASS_NAME_ID_DELIMITER}{self.pk}'

    def get_field_value(
        self,
        name: str,
    ):
        """
        Возвращает значение поля по имени
        """
        return self._fields[name]

    def set_field_value(
        self,
        name: str,
        value: str,
    ):
        """
        Установка значения поля у записи
        """
        self._fields[name] = value

    def _prepare_generic_foreign_key(
        self,
        generic_foreign_key: GenericForeignKey,
        content_type_cache: Dict[int, ContentType],
    ):
        """
        Подготовка GenericForeignKey для дальнейшего использования в
        Python-фикстурах
        """
        content_type_field_name = (
            generic_foreign_key.ct_field if
            generic_foreign_key.ct_field.endswith('_id') else
            f'{generic_foreign_key.ct_field}_id'
        )
        content_type_id = self.fields.get(content_type_field_name)
        object_id = self.fields.get(generic_foreign_key.fk_field)

        if content_type_id != 'None' and object_id != 'None':
            content_type = content_type_cache.get(int(content_type_id))
            model = apps.get_model(
                content_type.app_label,
                content_type.model
            )
            self._foreign_key_fields_map[generic_foreign_key.fk_field] = (
                model._meta.label
            )

    def _prepare_generic_foreign_keys(
        self,
        content_type_cache: Dict[int, ContentType],
    ):
        """
        Подготовка GenericForeignKey для дальнейшего использования в
        Python-фикстурах

        Подготовка подразумевает изменение типа поля object_id к ForeignKey для
        корректной подстановки фабрики. Это необходимо, т.к. при изменении
        идентификаторов в эталонной БД, например, при ее перегенерации
        """
        generic_foreign_keys = set(
            filter(
                lambda field: isinstance(field, GenericForeignKey),
                self.model_class._meta.private_fields
            )
        )

        for generic_foreign_key in generic_foreign_keys:
            self._prepare_generic_foreign_key(
                generic_foreign_key=generic_foreign_key,
                content_type_cache=content_type_cache,
            )

    def _prepare_foreign_key_fields_map(
        self,
        content_type_cache: Dict[int, ContentType],
    ):
        """
        Подготовка карты соответствия внешних ключей и моделей

        Необходимо определять карту для каждой записи, потому что они могут
        содержать GenericForeignKey или другие кастомные структуры, которые
        явно не являются внешними ключами, но подразумевают такое поведение
        """
        self._prepare_generic_foreign_keys(content_type_cache)

        prepare_record_foreign_key_fields_map_signal.send(
            sender=self,
        )

    def _prepare_fk_field_names(self):
        """
        Возвращает исчерпывающий список имен полей внешних ключей
        """
        return list(self._foreign_key_fields_map.keys())


class PreparingModelRecord:
    """
    Обрабатываемая запись модели
    """

    def __init__(
        self,
        model_record: ModelRecord,
        tag: int,
        changed_fields: Optional[Dict[str, Any]] = None,
        has_dependence: bool = False,
    ):
        self._model_record: ModelRecord = model_record
        self._tags: Set[int] = set()
        self._changed_fields: Optional[Dict[str, Any]] = None
        self._has_dependence = has_dependence

        self.set_tag(
            tag=tag,
            changed_fields=changed_fields,
        )

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} @model_record="{self._model_record}" '
            f'@tags="{", ".join(map(str, self._tags))}">'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def model_record(self) -> ModelRecord:
        return self._model_record

    @model_record.setter
    def model_record(self, model_record):
        self._model_record = model_record

    @property
    def tags(self) -> Set[int]:
        return self._tags

    @property
    def has_getting_tag(self):
        return PreparingModelRecordTagEnum.GETTING in self.tags

    @property
    def has_only_getting_tag(self):
        return (
            self.has_getting_tag and
            not self.has_creating_tag and
            not self.has_updating_tag and
            not self.has_deleting_tag
        )

    @property
    def has_creating_tag(self):
        return PreparingModelRecordTagEnum.CREATING in self.tags

    @property
    def has_no_creating_tag(self):
        return not self.has_creating_tag and (
            self.has_getting_tag or
            self.has_updating_tag or
            self.has_deleting_tag
        )

    @property
    def has_updating_tag(self):
        return PreparingModelRecordTagEnum.UPDATING in self.tags

    @property
    def has_deleting_tag(self):
        return PreparingModelRecordTagEnum.DELETING in self.tags

    @property
    def changed_fields(self) -> Optional[Dict[str, Any]]:
        return self._changed_fields

    @property
    def has_dependence(self):
        return self._has_dependence

    @has_dependence.setter
    def has_dependence(
        self,
        has_dependence: bool = False,
    ):
        self._has_dependence = has_dependence

    def set_tag(
        self,
        tag: int,
        changed_fields: Optional[Dict[str, Any]] = None,
    ):
        """
        Установка метки записи обратываемой записи. Метки влияют на действия с
        записями при выгрузке

        Если тег будет равен PreparingModelRecordTagEnum.UPDATING, то
        дополнительно устанавливаются измененные поля changed_fields

        Если у записи уже установлен тег из несовместимых
        PreparingModelRecordTagEnum.INCOMPATIBLES и совершается попытка
        добавить еще один, то об этом нужно оповестить пользователя
        """
        tag_is_incompatible = PreparingModelRecordTagEnum.is_incompatible(
            tag=tag,
        )

        if tag not in self._tags:
            if (
                tag_is_incompatible and
                PreparingModelRecordTagEnum.have_incompatible(self._tags)
            ):
                raise ValueError(
                    f'Can not set "{tag}" tag, because {self} already have '
                    f'incompatible tag!'
                )

            if (
                PreparingModelRecordTagEnum.is_updating(tag) and
                not changed_fields
            ):
                raise ValueError(
                    f'If you set UPDATING tag, you should send a changed '
                    f'fields dictionary.'
                )

            self._tags.add(tag)

            if PreparingModelRecordTagEnum.is_updating(tag):
                self._changed_fields = changed_fields

            if (
                PreparingModelRecordTagEnum.is_deleting(tag) or
                PreparingModelRecordTagEnum.is_updating(tag)
            ):
                self._tags.add(PreparingModelRecordTagEnum.GETTING)
