from rest_framework import serializers


class PrimaryKeyRelatedFieldFilterByUser(serializers.PrimaryKeyRelatedField):
    def __init__(self, user_field_name='user', **kwargs):
        self.user_field_name = user_field_name
        super().__init__(**kwargs)

    def get_queryset(self):
        return self.queryset.filter(**{
            self.user_field_name: self.context['request'].user
        })
