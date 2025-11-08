from django.dispatch import (
    Signal,
)


existing_factory_prepare_filter = Signal(providing_args=['factory_module_path'])
prepare_record_foreign_key_fields_map_signal = Signal()
