TAB_STR = '    '

MODEL_CLASS_NAME_ID_DELIMITER = FACTORY_CLASS_NAME_DELIMETER = '___'

IMPORT_TEMPLATE = 'from {import_path} import {class_name}'
IMPORT_WITH_ALIAS_TEMPLATE = 'from {import_path} import {class_name} as {class_name_alias}'  # noqa

EXCLUDED_FIELD_CLASSES = (
    'FileField',
)

GENERATED_PREFIX = 'Generated'
ACTUAL_PREFIX = 'Actual'
GENERATED_ACTUAL_PREFIX = 'GeneratedActual'

CONTENT_TYPE_MODEL = 'contenttypes.ContentType'


# Сдвиг значений первичных ключей записей сорцового хранилища при объединении
# двух хранилищ
PK_OFFSET = 100_000_000
