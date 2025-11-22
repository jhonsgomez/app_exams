from django.http import HttpResponseForbidden
from functools import wraps


def is_super_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden("No estás autenticado.")

        if user.role and user.role.name == "super_admin":
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("No tienes privilegios de administrador.")

    return _wrapped_view
