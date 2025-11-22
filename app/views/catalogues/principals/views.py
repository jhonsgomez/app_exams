from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import Principal
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone

@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    principals = Principal.objects.filter(deleted_at__isnull=True)

    if query:
        principals = principals.filter(Q(name__icontains=query))

    principals = principals.order_by("-created_at")

    paginator = Paginator(principals, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/principals/table.html", context)

@login_required(login_url="auth_login")
@is_admin
def create(request):
    return render(request, "catalogues/principals/form.html")

@login_required(login_url="auth_login")
@is_admin
def update(request, principal_id):
    if request.method == "GET":
        try:
            principal = get_object_or_404(Principal, pk=principal_id)
            return render(
                request,
                "catalogues/principals/form.html",
                {"principal": principal},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el rector: {str(e)}")
            return redirect("principals_table")

@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        principal_id = request.POST.get("principal_id")

        if principal_id:
            try:
                principal = get_object_or_404(Principal, pk=principal_id)
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("principals_update", principal_id=principal.pk)

                if (
                    Principal.objects.filter(name__iexact=name)
                    .exclude(pk=principal.pk)
                    .exists()
                ):
                    messages.error(request, "Ya existe un rector con ese nombre.")
                    return redirect("principals_update", principal_id=principal.pk)

                principal.name = name
                principal.save()
                messages.success(request, "Rector actualizado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar el rector: {str(e)}")

            return redirect("principals_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("principals_create")

                if Principal.objects.filter(name__iexact=name).exists():
                    messages.error(request, "Ya existe un rector con ese nombre.")
                    return redirect("principals_create")

                Principal.objects.create(name=name)
                messages.success(request, "Rector creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el rector: {str(e)}")

            return redirect("principals_table")

@login_required(login_url="auth_login")
@is_admin
def delete(request, principal_id):
    if request.method == "POST":
        try:
            principal = get_object_or_404(Principal, pk=principal_id)
            principal.deleted_at = timezone.now()
            principal.save()
            messages.success(request, "Rector eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el rector: {str(e)}")

    return redirect("principals_table")
