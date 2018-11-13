from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.utils import is_list_view
from rest_framework.schemas.generators import is_custom_action


class BulkingOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    The custom SchemaGenerator extended from drf_yasg schemagenerator to handle bulk operations
    """

    def get_operation_keys(self, subpath, method, view):
        """Return a list of keys that should be used to group an operation within the specification. ::

          /users/                   ("users", "list"), ("users", "create")
          /users/{pk}/              ("users", "read"), ("users", "update"), ("users", "delete")
          /users/enabled/           ("users", "enabled")  # custom viewset list action
          /users/{pk}/star/         ("users", "star")     # custom viewset detail action
          /users/{pk}/groups/       ("users", "groups", "list"), ("users", "groups", "create")
          /users/{pk}/groups/{pk}/  ("users", "groups", "read"), ("users", "groups", "update")

        :param str subpath: path to the operation with any common prefix/base path removed
        :param str method: HTTP method
        :param view: the view associated with the operation
        :rtype: tuple
        """
        if hasattr(view, 'action'):
            # Viewsets have explicitly named actions.
            action = view.action
        else:
            # Views have no associated action, so we determine one from the method.
            if is_list_view(subpath, method, view):
                action = 'list'
            else:
                action = self._gen.default_mapping[method.lower()]

        named_path_components = [
            component for component
            in subpath.strip('/').split('/')
            if '{' not in component
        ]

        if is_custom_action(action):
            # Custom action, eg "/users/{pk}/activate/", "/users/active/"
            if len(view.action_map) > 1:
                if not action.startswith(('bulk', 'partial_bulk')):
                    action = self._gen.default_mapping[method.lower()]

                if action in self._gen.coerce_method_names:
                    action = self._gen.coerce_method_names[action]

                return named_path_components + [action]
            else:
                return named_path_components[:-1] + [action]

        if action in self._gen.coerce_method_names:
            action = self._gen.coerce_method_names[action]

        # Default action, eg "/users/", "/users/{pk}/"
        return named_path_components + [action]
