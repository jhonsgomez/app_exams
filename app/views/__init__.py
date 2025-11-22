# Catalogues Routes
from .catalogues.modalities.views import (
    table as modalities_table,
    create as modalities_create,
    update as modalities_update,
    save as modalities_save,
    delete as modalities_delete,
)

from .catalogues.principals.views import (
    table as principals_table,
    create as principals_create,
    update as principals_update,
    save as principals_save,
    delete as principals_delete,
)

from .catalogues.representatives.views import (
    table as representatives_table,
    create as representatives_create,
    update as representatives_update,
    save as representatives_save,
    delete as representatives_delete,
)

from .catalogues.document_types.views import (
    table as document_types_table,
    create as document_types_create,
    update as document_types_update,
    save as document_types_save,
    delete as document_types_delete,
)

from .catalogues.institution_types.views import (
    table as institution_types_table,
    create as institution_types_create,
    update as institution_types_update,
    save as institution_types_save,
    delete as institution_types_delete,
)

from .catalogues.roles.views import (
    table as roles_table,
    create as roles_create,
    update as roles_update,
    save as roles_save,
    delete as roles_delete,
)

from .catalogues.groups.views import (
    table as groups_table,
    create as groups_create,
    update as groups_update,
    save as groups_save,
    delete as groups_delete,
)

# Dashboard Routes
from .dashboard.views import index as dashboard

# Auth Routes
from .auth.views import login, register, logout

# Institution Routes
from .institutions.views import (
    table as institutions_table,
    create as institutions_create,
    institution_info as institutions_info,
    update as institutions_update,
    save as institutions_save,
    delete as institutions_delete,
)

# Academic Routes
from .academic.views import (
    table as academic_departments_table,
    create as academic_departments_create,
    update as academic_departments_update,
    save as academic_departments_save,
    delete as academic_departments_delete,
)

# Question Routes
from .questions.difficulty.views import (
    table as difficulty_table,
    create as difficulty_create,
    update as difficulty_update,
    save as difficulty_save,
    delete as difficulty_delete,
)

from .questions.knowledge.views import (
    table as knowledge_table,
    create as knowledge_create,
    update as knowledge_update,
    save as knowledge_save,
    delete as knowledge_delete,
)

from .questions.bank.views import (
    table as questions_bank_table,
    create as questions_bank_create,
    update as questions_bank_update,
    save as questions_bank_save,
    deactivate as questions_bank_deactivate,
    activate as questions_bank_activate,
    delete as questions_bank_delete,
    questions as questions_bank_questions,
)

from .questions.question.views import (
    create as questions_create,
    update as questions_update,
    save as questions_save,
    deactivate as questions_deactivate,
    activate as questions_activate,
    delete as questions_delete,
)

# Exam Routes
from .exams.views import (
    table as exams_table,
    create as exams_create,
    update as exams_update,
    save as exams_save,
    deactivate as exams_deactivate,
    activate as exams_activate,
    delete as exams_delete,
    configure_sprt,
    exam_statistics,
)

# User Routes
from .users.admins.views import (
    table as admins_table,
    create as admins_create,
    update as admins_update,
    save as admins_save,
    activate as admins_activate,
    deactivate as admins_deactivate,
    delete as admins_delete,
)

from .users.students.views import (
    table as students_table,
    create as students_create,
    update as students_update,
    save as students_save,
    activate as students_activate,
    deactivate as students_deactivate,
    delete as students_delete,
)

# sprt views
from .sprt.views import (
    available_exams,
    start_attempt,
    take_attempt,
    submit_answer,
    attempt_results,
    my_attempts,
    abandon_attempt,
    exam_students,
    export_attempt_csv,
    export_exam_results,
)
