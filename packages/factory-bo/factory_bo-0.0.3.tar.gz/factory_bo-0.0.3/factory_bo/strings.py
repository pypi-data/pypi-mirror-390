from factory_bo.consts import (
    TAB_STR,
)


WRONG_FIXTURE_FILE_EXTENSION_ERROR = (
    'You should send absolute path of fixture file with .json extension, '
    'but send {destination_file_path}'
)

SEVERAL_MODEL_DAFAULT_FACTORIES_ERROR = (
    'Model "{model_label}" has several default factories: {factories}!'
)

WRONG_FACTORY_USE_TYPE_ERROR = (
    'Wrong factory use type "{factory_use_type}" of {factory_class_name}!'
)

PYTHON_FIXTURE_PATH_HAVE_NOT_PY_EXTENSION_ERROR = (
    'Python fuxture path have not .py extension - "{fixture_path}"!'
)

FACTORIES_FOR_MODEL_NOT_FOUND = (
    'Factories for model "{model_label}" not found.'
)

MODEL_WITHOUT_DEFAULT_FACTORY_ERROR = (
    'Models - ({model_labels}) without default factories!'
)

FACTORY_CLASS_FOR_MODEL_NOT_FOUND = (
    'Factory "{factory_class_name}" for model "{model_label}" not found!'
)

FACTORY_BO__FIXTURES_DIR_PATH_NOT_FOUND = (
    'Please set FIXTURES_DIR_PATH in the [factory_bo] section of'
    ' configuration file'
)

WRONG_DIFF_FORMAT = (
    'Wrong diff_format - "{}"! You can choose only py or sql formats.'
)

DISALLOWED_DJANGO_GET_OR_CREATE_FIELDS_FOUND_ERROR = (
    'Found dissallowed django_get_of_create fields - ({disallowed_fields}) of '
    'factory class "{factory_class}"!'
)

IMPORT_DEFAULT_MANAGER_FACTORY_STR = (
    f'from runner.factories.base import (\n{TAB_STR}DefaultManagerFactory,\n)\n'
)

NON_UNIQUE_DJANGO_GET_OR_CREATE_RECORD_FOUND_ERROR = (
    'Non unique django get or create record found error! Factory - '
    '{factory_class_name}, key - {key}'
)

FACTORY_CLASS_STR = (
    f'\n\n'
    f'class {{factory_class_name}}({{base_factory_class}}):\n'
    f'\n'
    f'{TAB_STR}class Meta:\n'
    f'{TAB_STR*2}model = \'{{model_label}}\'\n'
    f'{TAB_STR*2}# django_get_or_create = (\n'
    f'{{django_get_or_create_str}}\n'
    f'{TAB_STR*2}# )'
    f'\n'
)

FACTORY_CLASS_WITHOUT_COMMENT_STR = (
    f'\n\n'
    f'class {{factory_class_name}}({{base_factory_class}}):\n'
    f'\n'
    f'{TAB_STR}class Meta:\n'
    f'{TAB_STR*2}model = \'{{model_label}}\'\n'
    f'{TAB_STR*2}django_get_or_create = (\n'
    f'{{django_get_or_create_str}}\n'
    f'{TAB_STR*2})'
    f'\n'
)

IMPORT_FACTORY_USE_TYPE_ENUM_STR = (
    '\nfrom runner.factories.enums import FactoryUseTypeEnum'
)

USING_GENERATED_FACTORY_WARNING = (
    'Attention! You are use generated factory - "{generated_factory}"! Please '
    'actualize factory and remove "Generated" prefix.'
)

RECORD_FOR_FK_FIELD_NOT_FOUND_ERROR = (
    'For fk field "{field_name}" in model "{model_label}" related record '
    '"{related_record}" with id={field_value_id} in storage not found.'
    'Probably, problem is in hard binding to id in the old fixture.'
)
