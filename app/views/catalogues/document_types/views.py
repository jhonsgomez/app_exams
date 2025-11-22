from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import DocumentType
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    document_types = DocumentType.objects.filter(deleted_at__isnull=True)

    if query:
        document_types = document_types.filter(Q(name__icontains=query))

    document_types = document_types.order_by("-created_at")

    paginator = Paginator(document_types, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/document_types/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    return render(request, "catalogues/document_types/form.html")


@login_required(login_url="auth_login")
@is_super_admin
def update(request, document_type_id):
    if request.method == "GET":
        try:
            document_type = get_object_or_404(DocumentType, pk=document_type_id)
            return render(
                request,
                "catalogues/document_types/form.html",
                {"document_type": document_type},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el tipo de documento: {str(e)}")
            return redirect("document_types_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        document_type_id = request.POST.get("document_type_id")

        if document_type_id:
            try:
                document_type = get_object_or_404(DocumentType, pk=document_type_id)
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "document_types_update", document_type_id=document_type.pk
                    )

                if (
                    DocumentType.objects.filter(name__iexact=name)
                    .exclude(pk=document_type.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe otro tipo de documento con ese nombre."
                    )
                    return redirect(
                        "document_types_update", document_type_id=document_type.pk
                    )

                document_type.name = name
                document_type.save()
                messages.success(
                    request, "Tipo de documento actualizado correctamente."
                )

            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el tipo de documento: {str(e)}"
                )

            return redirect("document_types_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("document_types_create")

                if DocumentType.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe un tipo de documento con ese nombre."
                    )
                    return redirect("document_types_create")

                DocumentType.objects.create(name=name)
                messages.success(request, "Tipo de documento creado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al crear el tipo de documento: {str(e)}"
                )

            return redirect("document_types_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, document_type_id):
    if request.method == "POST":
        try:
            document_type = get_object_or_404(DocumentType, pk=document_type_id)
            document_type.deleted_at = timezone.now()
            document_type.save()
            messages.success(request, "Tipo de documento eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el tipo de documento: {str(e)}")

    return redirect("document_types_table")
