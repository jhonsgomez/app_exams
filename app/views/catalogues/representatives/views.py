from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import Representative
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    representatives = Representative.objects.filter(deleted_at__isnull=True)

    if query:
        representatives = representatives.filter(Q(name__icontains=query))

    representatives = representatives.order_by("-created_at")

    paginator = Paginator(representatives, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/representatives/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    return render(request, "catalogues/representatives/form.html")


@login_required(login_url="auth_login")
@is_admin
def update(request, representative_id):
    if request.method == "GET":
        try:
            representative = get_object_or_404(Representative, pk=representative_id)
            return render(
                request,
                "catalogues/representatives/form.html",
                {"representative": representative},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el representante: {str(e)}")
            return redirect("representatives_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        representative_id = request.POST.get("representative_id")

        if representative_id:
            try:
                representative = get_object_or_404(Representative, pk=representative_id)
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "representatives_update", representative_id=representative.pk
                    )

                if (
                    Representative.objects.filter(name__iexact=name)
                    .exclude(pk=representative.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe un representante con ese nombre."
                    )
                    return redirect(
                        "representatives_update", representative_id=representative.pk
                    )

                representative.name = name
                representative.save()
                messages.success(request, "Representante actualizado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el representante: {str(e)}"
                )

            return redirect("representatives_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("representatives_create")

                if Representative.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe un representante con ese nombre."
                    )
                    return redirect("representatives_create")

                Representative.objects.create(name=name)
                messages.success(request, "Representante creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el representante: {str(e)}")

            return redirect("representatives_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, representative_id):
    if request.method == "POST":
        try:
            representative = get_object_or_404(Representative, pk=representative_id)
            representative.deleted_at = timezone.now()
            representative.save()
            messages.success(request, "Representante eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el representante: {str(e)}")

    return redirect("representatives_table")
