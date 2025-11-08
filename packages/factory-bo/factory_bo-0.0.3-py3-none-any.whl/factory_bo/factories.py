from typing import (
    Optional,
    Type,
)

from django.db.models import (
    Model,
)

from factory_bo.base import (
    DefaultManagerFactory,
)


class ExistingFactory:
    """
    Класс существующей фабрики
    """
    def __init__(
        self,
        factory_class,
        import_path: str,
        module_path: str,
        factory_class_name_alias: str = None,
    ):
        self._factory_class = factory_class
        self._factory_class_name_alias = factory_class_name_alias
        self._import_path = import_path
        self._module_path = module_path

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} '
            f'@model_label="{self.factory_model_label}" '
            f'@factory_class_name="{self.factory_class_name}">'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def factory_class(self) -> Type[DefaultManagerFactory]:
        return self._factory_class

    @property
    def factory_class_name_alias(self) -> Optional[str]:
        return self._factory_class_name_alias

    @factory_class_name_alias.setter
    def factory_class_name_alias(
        self,
        value: str,
    ):
        self._factory_class_name_alias = value

    @property
    def factory_class_name(self) -> str:
        """
        Возвращает имя класса фабрики или алиас, если он задан
        """
        return self._factory_class_name_alias or self._factory_class.__name__

    @property
    def factory_model(self) -> Type[Model]:
        return self._factory_class.get_model()

    @property
    def factory_model_label(self) -> str:
        return self._factory_class.get_model_label()

    @property
    def import_path(self):
        return self._import_path

    @property
    def module_path(self):
        return self._module_path

    @property
    def get_or_create_fields(self):
        return self._factory_class.get_django_get_or_create()

    @property
    def auto_updated_fields(self):
        return self._factory_class.get_auto_updated_fields()

    @property
    def allow_use_id_field(self):
        return self._factory_class.get_allow_use_id_field()

    @property
    def excluded_fk_fields(self):
        return self._factory_class.get_excluded_fk_fields()
