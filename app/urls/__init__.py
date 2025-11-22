from .academic.urls import urlpatterns as academic_urls
from .auth.urls import urlpatterns as auth_urls

from .dashboard.urls import urlpatterns as dashboard_urls

from .catalogues.document_types.urls import urlpatterns as document_types_urls
from .catalogues.groups.urls import urlpatterns as groups_urls
from .catalogues.institution_types.urls import urlpatterns as institution_types_urls
from .catalogues.modalities.urls import urlpatterns as modalities_urls
from .catalogues.principals.urls import urlpatterns as principals_urls
from .catalogues.representatives.urls import urlpatterns as representatives_urls
from .catalogues.roles.urls import urlpatterns as roles_urls

from .institutions.urls import urlpatterns as institution_urls

from .questions.difficulty.urls import urlpatterns as difficulty_urls
from .questions.knowledge.urls import urlpatterns as knowledge_urls
from .questions.bank.urls import urlpatterns as questions_bank_urls
from .questions.question.urls import urlpatterns as questions_urls

from .exams.urls import urlpatterns as exams_urls

from .users.admins.urls import urlpatterns as admins_urls
from .users.students.urls import urlpatterns as students_urls

from .sprt.urls import urlpatterns as sprt_urls