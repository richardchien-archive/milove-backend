from rest_framework import exceptions as rest_exceptions


def validate_or_raise(form_or_serializer):
    if not form_or_serializer.is_valid():
        raise rest_exceptions.ValidationError(detail=form_or_serializer.errors)
