from django.db.models import signals
from django.dispatch import receiver


@receiver(signals.pre_save)
def models_pre_save(sender, instance, **_):
    if not sender.__module__.startswith('milove.shop.models'):
        # ignore models of other apps
        return

    # noinspection PyProtectedMember
    fields = sender._meta.local_fields

    # 'changed' trigger
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)

        for field in fields:
            # noinspection PyBroadException
            try:
                func = getattr(sender, field.name + '_changed', None)  # class function or static function
                if func and callable(func) and getattr(old, field.name, None) != getattr(instance, field.name, None):
                    # field has changed
                    func(old, instance)
            except:
                pass

    # 'default' trigger
    for field in fields:
        # noinspection PyBroadException
        try:
            func = getattr(sender, field.name + '_default', None)  # class function or static function
            if func and callable(func) and not getattr(instance, field.name):
                default_val = func(instance)
                if default_val is not None:
                    setattr(instance, field.name, default_val)
        except:
            pass
