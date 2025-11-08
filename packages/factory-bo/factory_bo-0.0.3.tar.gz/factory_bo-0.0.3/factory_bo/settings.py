
def init(conf):
    # =============================================================================
    # Настройки factory_bo.
    # =============================================================================
    FIXTURES_DIR_PATH = conf.get(
        'factory_bo',
        'FIXTURES_DIR_PATH'
    )

    # Исключаемые из обработки приложения
    EXCLUDED_APPS = conf.get(
        'factory_bo',
        'EXCLUDED_APPS'
    )
    if EXCLUDED_APPS:
        EXCLUDED_APPS = set(
            map(
                lambda x: x.strip(),
                EXCLUDED_APPS.split(',')
            )
        )
    else:
        EXCLUDED_APPS = set()

    # Исключаемые из обработки модели
    EXCLUDED_MODELS = conf.get(
        'factory_bo',
        'EXCLUDED_MODELS'
    )
    if EXCLUDED_MODELS:
        EXCLUDED_MODELS = set(
            map(
                lambda x: x.strip(),
                EXCLUDED_MODELS.split(',')
            )
        )
    else:
        EXCLUDED_MODELS = set()

    # Поля-идентификаторы полей моделей содержащих ссылки на ту же модель
    PSEUDO_SELF_FK_IDS = conf.get(
        'factory_bo',
        'PSEUDO_SELF_FK_IDS'
    )
    if PSEUDO_SELF_FK_IDS:
        PSEUDO_SELF_FK_IDS = list(
            map(
                lambda x: x.strip(),
                PSEUDO_SELF_FK_IDS.split(',')
            )
        )
    else:
        PSEUDO_SELF_FK_IDS = []

    # Поля-идентификаторы, которые являются псевдо внешними ключами на
    # существующие записи таблиц. Значения представляют из себя строки
    # содержащие: имя поля, разделитель в виде трех подчеркиваний, метка
    # модели (Model._meta.label). Например, ent_id___enterprise.Enterprise
    PSEUDO_FK_IDS = conf.get(
        'factory_bo',
        'PSEUDO_FK_IDS'
    )
    if PSEUDO_FK_IDS:
        PSEUDO_FK_IDS = dict(
            map(
                lambda x: x.strip().split('___'),
                PSEUDO_FK_IDS.split(',')
            )
        )
    else:
        PSEUDO_FK_IDS = {}

    return {
        'FIXTURES_DIR_PATH': FIXTURES_DIR_PATH,
        'EXCLUDED_APPS': EXCLUDED_APPS,
        'EXCLUDED_MODELS': EXCLUDED_MODELS,
        'PSEUDO_SELF_FK_IDS': PSEUDO_SELF_FK_IDS,
        'PSEUDO_FK_IDS': PSEUDO_FK_IDS,
    }
