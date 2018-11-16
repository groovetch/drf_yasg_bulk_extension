from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.inspectors import SwaggerAutoSchema as BaseSwaggerAutoSchema
from drf_yasg.utils import guess_response_status, is_list_view
from rest_framework.request import is_form_media_type


def is_bulk_view(path, method, view):
    if not is_list_view(path, method, view):
        return False

    return hasattr(view, 'action') and view.action.startswith(('bulk', 'partial_bulk'))


class SwaggerAutoSchema(BaseSwaggerAutoSchema):
    def get_request_body_parameters(self, consumes):
        """Return the request body parameters for this view. |br|
        This is either:

        -  a list with a single object Parameter with a :class:`.Schema` derived from the request serializer
        -  a list of primitive Parameters parsed as form data

        :param list[str] consumes: a list of accepted MIME types as returned by :meth:`.get_consumes`
        :return: a (potentially empty) list of :class:`.Parameter`\\ s either ``in: body`` or ``in: formData``
        :rtype: list[openapi.Parameter]
        """
        serializer = self.get_request_serializer()
        schema = None
        if serializer is None:
            return []

        if isinstance(serializer, openapi.Schema.OR_REF):
            schema = serializer

        if any(is_form_media_type(encoding) for encoding in consumes):
            if schema is not None:
                raise SwaggerGenerationError("form request body cannot be a Schema")
            return self.get_request_form_parameters(serializer)
        else:
            if schema is None:
                schema = self.get_request_body_schema(serializer)
                # Small change to handle bulk api, convert request to list of model
                if hasattr(self.view, 'action') and self.view.action.startswith(('bulk', 'partial_bulk')):
                    schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=schema)

            return [self.make_body_parameter(schema)] if schema is not None else []

    def get_default_responses(self):
        """Get the default responses determined for this view from the request serializer and request method.

        :type: dict[str, openapi.Schema]
        """
        method = self.method.lower()

        default_status = guess_response_status(method)
        default_schema = ''
        if method in ('get', 'post', 'put', 'patch'):
            default_schema = self.get_default_response_serializer()

        default_schema = default_schema or ''
        if default_schema and not isinstance(default_schema, openapi.Schema):
            default_schema = self.serializer_to_schema(default_schema) or ''

        if default_schema:
            if (is_list_view(self.path, self.method, self.view) and self.method.lower() == 'get') \
                    or is_bulk_view(self.path, self.method, self.view):
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paginated_response(default_schema) or default_schema

        return OrderedDict({str(default_status): default_schema})

    def should_filter(self):
        """Determine whether filter backend parameters should be included for this request.

        :rtype: bool
        """
        if not getattr(self.view, 'filter_backends', None):
            return False

        if getattr(self.view, 'action', '') in ('bulk_destroy',):
            return False

        if self.method.lower() not in ["get", "delete"]:
            return False

        return is_list_view(self.path, self.method, self.view)
