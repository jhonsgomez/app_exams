from django.shortcuts import render, redirect
from app.models import (
    Institution,
    AcademicDepartment,
    Group,
    DocumentType,
    CustomUser,
    Role,
)
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "GET":
        return render(request, "auth/login.html")
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "El correo y la contraseña son obligatorios.")
            return redirect("auth_login")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active and not user.deleted_at:
                auth_login(request, user)
                welcome_name = user.first_name
                if user.last_name:
                    welcome_name += f" {user.last_name}"
                messages.success(request, f"Bienvenido {welcome_name}")
                return redirect("dashboard")
            else:
                messages.error(request, "Tu cuenta está inactiva.")
        else:
            messages.error(request, "Credenciales incorrectas.")

        return redirect("auth_login")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "GET":
        institutions = Institution.objects.filter(deleted_at__isnull=True)
        academic_departments = AcademicDepartment.objects.filter(
            deleted_at__isnull=True
        )
        groups = Group.objects.filter(deleted_at__isnull=True)
        document_types = DocumentType.objects.filter(deleted_at__isnull=True)

        return render(
            request,
            "auth/register.html",
            {
                "institutions": institutions,
                "academic_departments": academic_departments,
                "groups": groups,
                "document_types": document_types,
            },
        )
    elif request.method == "POST":
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
                return redirect("auth_register")

            if not email:
                messages.error(request, "El email es obligatorio.")
                return redirect("auth_register")

            if not institution_id:
                messages.error(request, "La institución es obligatoria.")
                return redirect("auth_register")

            if not document_type_id:
                messages.error(request, "El tipo de documento es obligatorio.")
                return redirect("auth_register")

            if not document_number:
                messages.error(request, "El número de documento es obligatorio.")
                return redirect("auth_register")

            if CustomUser.objects.filter(
                document_number=document_number, deleted_at__isnull=True
            ).exists():
                messages.error(
                    request, "El número de documento ya pertenece a otro usuario."
                )
                return redirect("auth_register")

            if CustomUser.objects.filter(email=email, deleted_at__isnull=True).exists():
                messages.error(request, "El email ya pertenece a otro usuario.")
                return redirect("auth_register")

            if institution_id:
                institution = Institution.objects.get(pk=institution_id)
                if institution.institution_type.id == 3 and not group_id:
                    messages.error(request, "El grupo es obligatorio para colegios.")
                    return redirect("auth_register")
                elif institution.institution_type.id != 3:
                    if not academic_department_id:
                        messages.error(
                            request,
                            "El departamento académico es obligatorio para universidades.",
                        )
                        return redirect("auth_register")
                    if not semester:
                        messages.error(
                            request,
                            "El semestre es obligatorio para universidades.",
                        )
                        return redirect("auth_register")

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

            messages.success(
                request, "Cuenta creada correctamente. Ahora puedes iniciar sesión."
            )
        except Exception as e:
            messages.error(request, f"Error al crear la cuenta: {str(e)}")

        return redirect("auth_login")


def logout(request):
    auth_logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("index")
