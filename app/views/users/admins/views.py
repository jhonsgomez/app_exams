from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import CustomUser, Institution, Role
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    admins = CustomUser.objects.filter(role__name="admin", deleted_at__isnull=True)

    if query:
        admins = admins.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    admins = admins.order_by("-created_at")

    paginator = Paginator(admins, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "users/admins/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    institutions = Institution.objects.filter(deleted_at__isnull=True)

    return render(
        request,
        "users/admins/form.html",
        {
            "institutions": institutions,
        },
    )


@login_required(login_url="auth_login")
@is_super_admin
def update(request, admin_id):
    if request.method == "GET":
        try:
            admin = get_object_or_404(CustomUser, pk=admin_id)
            institutions = Institution.objects.filter(deleted_at__isnull=True)

            return render(
                request,
                "users/admins/form.html",
                {
                    "admin": admin,
                    "institutions": institutions,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al encontrar el administrador: {str(e)}")
            return redirect("admins_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        admin_id = request.POST.get("admin_id")

        if admin_id:
            try:
                admin = get_object_or_404(CustomUser, pk=admin_id)
                first_name = request.POST.get("first_name").strip()
                last_name = request.POST.get("last_name").strip()
                email = request.POST.get("email").strip()
                password = request.POST.get("password").strip()
                institution_id = request.POST.get("institution").strip()

                if not first_name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("admins_update", admin_id=admin_id)

                if not email:
                    messages.error(request, "El correo electrónico es obligatorio.")
                    return redirect("admins_update", admin_id=admin_id)

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("admins_update", admin_id=admin_id)

                if password:
                    if len(password) < 8:
                        messages.error(
                            request, "La contraseña debe tener al menos 8 caracteres."
                        )
                        return redirect("admins_update", admin_id=admin_id)

                admin.first_name = first_name
                admin.last_name = last_name
                admin.email = email
                admin.institution_id = institution_id
                if password:
                    admin.set_password(password)

                admin.updated_at = timezone.now()
                admin.save()

                messages.success(request, "Administrador actualizado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el administrador: {str(e)}"
                )

            return redirect("admins_table")
        else:
            try:
                first_name = request.POST.get("first_name").strip()
                last_name = request.POST.get("last_name").strip()
                email = request.POST.get("email").strip()
                password = request.POST.get("password").strip()
                institution_id = request.POST.get("institution").strip()

                if not first_name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("admins_create")

                if not email:
                    messages.error(request, "El correo electrónico es obligatorio.")
                    return redirect("admins_create")

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("admins_create")

                if password:
                    if len(password) < 8:
                        messages.error(
                            request, "La contraseña debe tener al menos 8 caracteres."
                        )
                        return redirect("admins_create")

                role = Role.objects.get(name="admin")

                CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    role=role,
                    first_name=first_name,
                    last_name=last_name,
                    institution_id=institution_id,
                )

                messages.success(request, "Administrador creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el administrador: {str(e)}")

            return redirect("admins_table")


@login_required(login_url="auth_login")
@is_super_admin
def activate(request, admin_id):
    if request.method == "GET":
        try:
            admin = get_object_or_404(CustomUser, pk=admin_id)
            admin.is_active = True
            admin.save()

            messages.success(request, "Administrador activado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al activar el administrador: {str(e)}")

    return redirect("admins_table")


@login_required(login_url="auth_login")
@is_super_admin
def deactivate(request, admin_id):
    if request.method == "GET":
        try:
            admin = get_object_or_404(CustomUser, pk=admin_id)
            admin.is_active = False
            admin.save()

            messages.success(request, "Administrador desactivado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al desactivar el administrador: {str(e)}")

    return redirect("admins_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, admin_id):
    if request.method == "POST":
        try:
            admin = get_object_or_404(CustomUser, pk=admin_id)
            admin.deleted_at = timezone.now()
            admin.save()

            messages.success(request, "Administrador eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el administrador: {str(e)}")

    return redirect("admins_table")
