from django.apps import (
    apps,
)
from django.core.management import (
    BaseCommand,
)
from django.db.models import (
    ForeignKey,
)


class Command(BaseCommand):
    """
    Команда для поиска циклических зависимостей на уровне таблиц
    """
    def handle(self, *args, **options):
        models = apps.get_models(include_auto_created=True)
        model_relation_pairs = set()

        for model in models:
            for field in model._meta.fields:
                if (
                    isinstance(field, ForeignKey) and
                    model._meta.label != field.related_model._meta.label
                ):
                    model_relation_pairs.add(
                        (
                            model._meta.label,
                            field.related_model._meta.label
                        )
                    )

        for model1, model2 in model_relation_pairs:
            if (model2, model1) in model_relation_pairs:
                print(f'{model2},{model1}')
