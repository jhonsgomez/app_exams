from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import (
    CustomUser,
    Institution,
    AcademicDepartment,
    Group,
    DocumentType,
    Role,
)
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    students = CustomUser.objects.filter(
        role__name="estudiante", deleted_at__isnull=True
    )

    if request.user.institution:
        students = students.filter(institution=request.user.institution)

    if query:
        students = students.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(document_number__icontains=query)
        )

    students = students.order_by("-created_at")

    paginator = Paginator(students, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "users/students/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    institutions = Institution.objects.filter(deleted_at__isnull=True)
    academic_departments = AcademicDepartment.objects.filter(deleted_at__isnull=True)
    groups = Group.objects.filter(deleted_at__isnull=True)
    document_types = DocumentType.objects.filter(deleted_at__isnull=True)

    return render(
        request,
        "users/students/form.html",
        {
            "institutions": institutions,
            "academic_departments": academic_departments,
            "groups": groups,
            "document_types": document_types,
        },
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, student_id):
    if request.method == "GET":
        student = get_object_or_404(CustomUser, pk=student_id)
        institutions = Institution.objects.filter(deleted_at__isnull=True)
        academic_departments = AcademicDepartment.objects.filter(
            deleted_at__isnull=True
        )
        groups = Group.objects.filter(deleted_at__isnull=True)
        document_types = DocumentType.objects.filter(deleted_at__isnull=True)

        return render(
            request,
            "users/students/form.html",
            {
                "student": student,
                "institutions": institutions,
                "academic_departments": academic_departments,
                "groups": groups,
                "document_types": document_types,
            },
        )


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")

        if student_id:
            try:
                student = get_object_or_404(CustomUser, pk=student_id)
                first_name = request.POST.get("first_name")
                if first_name:
                    first_name = first_name.strip()
                last_name = request.POST.get("last_name")
                if last_name:
                    last_name = last_name.strip()
                email = request.POST.get("email")
                if email:
                    email = email.strip()
                institution_id = request.POST.get("institution")
                if institution_id:
                    institution_id = institution_id.strip()
                academic_department_id = request.POST.get("academic_department")
                if academic_department_id:
                    academic_department_id = academic_department_id.strip()
                group_id = request.POST.get("group")
                if group_id:
                    group_id = group_id.strip()
                document_type_id = request.POST.get("document_type")
                if document_type_id:
                    document_type_id = document_type_id.strip()
                document_number = request.POST.get("document_number")
                if document_number:
                    document_number = document_number.strip()
                phone = request.POST.get("phone")
                if phone:
                    phone = phone.strip()
                semester = request.POST.get("semester")
                if semester:
                    semester = semester.strip()
                else:
                    semester = None

                if not first_name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("students_update", student_id=student_id)

                if not email:
                    messages.error(request, "El email es obligatorio.")
                    return redirect("students_update", student_id=student_id)

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("students_update", student_id=student_id)

                if not document_type_id:
                    messages.error(request, "El tipo de documento es obligatorio.")
                    return redirect("students_update", student_id=student_id)

                if not document_number:
                    messages.error(request, "El número de documento es obligatorio.")
                    return redirect("students_update", student_id=student_id)

                if (
                    CustomUser.objects.filter(
                        document_number=document_number, deleted_at__isnull=True
                    )
                    .exclude(pk=student_id)
                    .exists()
                ):
                    messages.error(
                        request, "El número de documento ya pertenece a otro usuario."
                    )
                    return redirect("students_update", student_id=student_id)

                if (
                    CustomUser.objects.filter(email=email, deleted_at__isnull=True)
                    .exclude(pk=student_id)
                    .exists()
                ):
                    messages.error(request, "El email ya pertenece a otro usuario.")
                    return redirect("students_update", student_id=student_id)

                if institution_id:
                    institution = Institution.objects.get(pk=institution_id)
                    if institution.institution_type.id == 3 and not group_id:
                        messages.error(
                            request, "El grupo es obligatorio para colegios."
                        )
                        return redirect("students_update", student_id=student_id)
                    elif institution.institution_type.id != 3:
                        if not academic_department_id:
                            messages.error(
                                request,
                                "El departamento académico es obligatorio para universidades.",
                            )
                            return redirect("students_update", student_id=student_id)
                        if not semester:
                            messages.error(
                                request,
                                "El semestre es obligatorio para universidades.",
                            )
                            return redirect("students_update", student_id=student_id)

                role = Role.objects.get(name="estudiante")

                student.first_name = first_name
                student.last_name = last_name
                student.email = email
                student.role = role
                student.institution_id = institution_id
                student.academic_department_id = academic_department_id
                student.group_id = group_id
                student.document_type_id = document_type_id
                student.document_number = document_number
                student.phone = phone
                student.semester = semester
                student.is_active = True
                student.updated_at = timezone.now()

                student.set_password(document_number)
                student.save()

                messages.success(request, "Estudiante actualizado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar el estudiante: {str(e)}")

            return redirect("students_table")
        else:
            try:
                first_name = request.POST.get("first_name")
                if first_name:
                    first_name = first_name.strip()
                last_name = request.POST.get("last_name")
                if last_name:
                    last_name = last_name.strip()
                email = request.POST.get("email")
                if email:
                    email = email.strip()
                institution_id = request.POST.get("institution")
                if institution_id:
                    institution_id = institution_id.strip()
                academic_department_id = request.POST.get("academic_department")
                if academic_department_id:
                    academic_department_id = academic_department_id.strip()
                group_id = request.POST.get("group")
                if group_id:
                    group_id = group_id.strip()
                document_type_id = request.POST.get("document_type")
                if document_type_id:
                    document_type_id = document_type_id.strip()
                document_number = request.POST.get("document_number")
                if document_number:
                    document_number = document_number.strip()
                phone = request.POST.get("phone")
                if phone:
                    phone = phone.strip()
                semester = request.POST.get("semester")
                if semester:
                    semester = semester.strip()
                else:
                    semester = None

                if not first_name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("students_create")

                if not email:
                    messages.error(request, "El email es obligatorio.")
                    return redirect("students_create")

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("students_create")

                if not document_type_id:
                    messages.error(request, "El tipo de documento es obligatorio.")
                    return redirect("students_create")

                if not document_number:
                    messages.error(request, "El número de documento es obligatorio.")
                    return redirect("students_create")

                if (
                    CustomUser.objects.filter(
                        document_number=document_number, deleted_at__isnull=True
                    )
                    .exclude(pk=student_id)
                    .exists()
                ):
                    messages.error(
                        request, "El número de documento ya pertenece a otro usuario."
                    )
                    return redirect("students_create")

                if (
                    CustomUser.objects.filter(email=email, deleted_at__isnull=True)
                    .exclude(pk=student_id)
                    .exists()
                ):
                    messages.error(request, "El email ya pertenece a otro usuario.")
                    return redirect("students_create")

                if institution_id:
                    institution = Institution.objects.get(pk=institution_id)
                    if institution.institution_type.id == 3 and not group_id:
                        messages.error(
                            request, "El grupo es obligatorio para colegios."
                        )
                        return redirect("students_create")
                    elif institution.institution_type.id != 3:
                        if not academic_department_id:
                            messages.error(
                                request,
                                "El departamento académico es obligatorio para universidades.",
                            )
                            return redirect("students_create")
                        if not semester:
                            messages.error(
                                request,
                                "El semestre es obligatorio para universidades.",
                            )
                            return redirect("students_create")

                role = Role.objects.get(name="estudiante")

                student = CustomUser.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=role,
                    institution_id=institution_id,
                    academic_department_id=academic_department_id,
                    group_id=group_id,
                    document_type_id=document_type_id,
                    document_number=document_number,
                    phone=phone,
                    semester=semester,
                    is_active=True,
                )

                student.set_password(document_number)
                student.save()

                messages.success(request, "Estudiante creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el estudiante: {str(e)}")

            return redirect("students_table")


@login_required(login_url="auth_login")
@is_admin
def activate(request, student_id):
    if request.method == "GET":
        try:
            student = get_object_or_404(CustomUser, pk=student_id)
            student.is_active = True
            student.updated_at = timezone.now()
            student.save()
            messages.success(request, "Estudiante activado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al activar el estudiante: {str(e)}")

        return redirect("students_table")


@login_required(login_url="auth_login")
@is_admin
def deactivate(request, student_id):
    if request.method == "GET":
        try:
            student = get_object_or_404(CustomUser, pk=student_id)
            student.is_active = False
            student.updated_at = timezone.now()
            student.save()
            messages.success(request, "Estudiante desactivado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al desactivar el estudiante: {str(e)}")

        return redirect("students_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, student_id):
    if request.method == "POST":
        try:
            student = get_object_or_404(CustomUser, pk=student_id)
            student.deleted_at = timezone.now()
            student.save()
            messages.success(request, "Estudiante eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el estudiante: {str(e)}")

        return redirect("students_table")
