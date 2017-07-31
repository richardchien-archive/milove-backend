from rest_framework import exceptions as rest_exceptions
from rest_framework.viewsets import mixins


def validate_or_raise(form_or_serializer):
    if not form_or_serializer.is_valid():
        raise rest_exceptions.ValidationError(detail=form_or_serializer.errors)


class PartialUpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            # entire update is not allowed
            raise rest_exceptions.MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)
