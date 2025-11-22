from .catalogues.models import (
    Role,
    InstitutionType,
    DocumentType,
    Modality,
    Representative,
    Principal,
    Group,
)

from .institution.models import Institution
from .academic.models import AcademicDepartment, AcademicLevel
from .questions.models import (
    DifficultyLevel,
    KnowledgeArea,
    QuestionBank,
    Question,
    AnswerOption,
)
from .exams.models import Exam
from .user.models import CustomUser

from .sprt.models import (
    ExamSPRTConfig,
    ExamAttempt,
    AttemptAnswer,
    LevelProgress,
)
