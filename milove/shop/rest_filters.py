from django_filters import rest_framework as filters


class CommaSplitListFilter(filters.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(distinct=True, *args, **kwargs)

    def filter(self, qs, value):
        value_list = value.split(',')
        self.lookup_expr = 'in'
        return super().filter(qs, value_list)
