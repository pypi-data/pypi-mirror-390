from collections import (
    defaultdict,
)

from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
)


class Command(BaseCommand):
    """
    Проверяет целостность данных, в части использования self fk полей
    """

    def handle(self, *args, **options):
        SELF_FK_IDS = (
            'external_id',
            'direct_id',
            'root_id',
            'parent_id',
        )

        models = apps.get_models(include_auto_created=True)
        model_self_fks = defaultdict(dict)

        for model in models:
            if 'web-bb-salary' in model._meta.app_config.path:
                model.objects = model._base_manager

                fields_list = (
                    field.attname
                    for field in model._meta.fields
                )

                self_fks = set(SELF_FK_IDS).intersection(fields_list)

                if self_fks:
                    for self_fk in self_fks:
                        model_self_fks[model._meta.label][self_fk] = set()

                        self_fk_ids = set(
                            model.objects.exclude(
                                **{
                                    f'{self_fk}__isnull': True,
                                }
                            ).values_list(self_fk, flat=True)
                        )

                        if self_fk_ids:
                            for self_fk_id in self_fk_ids:
                                try:
                                    model.objects.get(
                                        **{
                                            'pk': self_fk_id,
                                        }
                                    )
                                except model.DoesNotExist:
                                    model_self_fks[model._meta.label][self_fk].add(
                                        self_fk_id
                                    )

        file_path = (
            f'{settings.FACTORY_BO__FIXTURES_DIR_PATH}/'
            f'salary_db_self_fks_consistency.csv'
        )
        with open(file_path, 'w') as f:
            for model_label, self_fks_dict in model_self_fks.items():
                for self_fk, self_fk_ids in self_fks_dict.items():
                    if self_fk_ids:
                        f.write(f'{model_label},{self_fk}\n')
                        for self_fk_id in self_fk_ids:
                            f.write(f',{self_fk_id}\n')
