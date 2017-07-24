from django_filters import rest_framework as filters


class CommaSplitListFilter(filters.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        value_list = value.split(',')
        return qs.filter(**{self.name + '__in': value_list})
