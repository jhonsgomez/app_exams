from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import Role
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    roles = Role.objects.filter(deleted_at__isnull=True).exclude(
        name__in=["super_admin", "admin"]
    )

    if query:
        roles = roles.filter(Q(name__icontains=query))

    roles = roles.order_by("-created_at")

    paginator = Paginator(roles, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/roles/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    return render(request, "catalogues/roles/form.html")


@login_required(login_url="auth_login")
@is_super_admin
def update(request, role_id):
    if request.method == "GET":
        try:
            role = get_object_or_404(Role, pk=role_id)
            return render(
                request,
                "catalogues/roles/form.html",
                {"role": role},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el rol: {str(e)}")
            return redirect("roles_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        role_id = request.POST.get("role_id")

        if role_id:
            try:
                role = get_object_or_404(Role, pk=role_id)
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("roles_update", role_id=role.pk)

                if Role.objects.filter(name__iexact=name).exclude(pk=role.pk).exists():
                    messages.error(request, "Ya existe un rol con ese nombre.")
                    return redirect("roles_update", role_id=role.pk)

                role.name = name
                role.save()
                messages.success(request, "Rol actualizado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar el rol: {str(e)}")

            return redirect("roles_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("roles_create")

                if Role.objects.filter(name__iexact=name).exists():
                    messages.error(request, "Ya existe un rol con ese nombre.")
                    return redirect("roles_create")

                Role.objects.create(name=name)
                messages.success(request, "Rol creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el rol: {str(e)}")

            return redirect("roles_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, role_id):
    if request.method == "POST":
        try:
            role = get_object_or_404(Role, pk=role_id)
            role.deleted_at = timezone.now()
            role.save()
            messages.success(request, "Rol eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el rol: {str(e)}")

    return redirect("roles_table")
