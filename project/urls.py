from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from urls import index_urls
from app.urls import (
    dashboard_urls,
    academic_urls,
    auth_urls,
    document_types_urls,
    groups_urls,
    institution_types_urls,
    modalities_urls,
    principals_urls,
    representatives_urls,
    roles_urls,
    institution_urls,
    difficulty_urls,
    knowledge_urls,
    questions_bank_urls,
    questions_urls,
    exams_urls,
    admins_urls,
    students_urls,
    
    sprt_urls,
)

urlpatterns = [
    path("", include(index_urls)),
    path("dashboard/", include(dashboard_urls)),
    path("academic-departments/", include(academic_urls)),
    path("auth/", include(auth_urls)),
    path("document-types/", include(document_types_urls)),
    path("groups/", include(groups_urls)),
    path("institution-types/", include(institution_types_urls)),
    path("modalities/", include(modalities_urls)),
    path("principals/", include(principals_urls)),
    path("representatives/", include(representatives_urls)),
    path("roles/", include(roles_urls)),
    path("institutions/", include(institution_urls)),
    path("difficulty/", include(difficulty_urls)),
    path("knowledge/", include(knowledge_urls)),
    path("questions-bank/", include(questions_bank_urls)),
    path("questions/", include(questions_urls)),
    path("exams/", include(exams_urls)),
    path("admins/", include(admins_urls)),
    path("students/", include(students_urls)),
    
    path("sprt/", include(sprt_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
