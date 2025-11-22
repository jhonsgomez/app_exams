from typing import Dict
from app.models import ExamAttempt


def generate_exam_report(attempt: ExamAttempt) -> Dict:
    """
    Genera un reporte completo de un intento de examen.

    Args:
        attempt: Instancia del intento

    Returns:
        Diccionario con datos del reporte
    """
    answers = attempt.answers.all().order_by("question_number")

    # Análisis por área de conocimiento
    area_analysis = {}
    for answer in answers:
        area_name = (
            answer.question.knowledge_area.name
            if answer.question.knowledge_area
            else "Sin área"
        )

        if area_name not in area_analysis:
            area_analysis[area_name] = {"total": 0, "correct": 0, "incorrect": 0}

        area_analysis[area_name]["total"] += 1
        if answer.is_correct:
            area_analysis[area_name]["correct"] += 1
        else:
            area_analysis[area_name]["incorrect"] += 1

    # Calcular precisión por área
    for area_name in area_analysis:
        total = area_analysis[area_name]["total"]
        correct = area_analysis[area_name]["correct"]
        area_analysis[area_name]["accuracy"] = (
            (correct / total * 100) if total > 0 else 0
        )

    # Análisis temporal
    time_analysis = {
        "total_time": sum(a.time_taken_seconds for a in answers),
        "avg_time_per_question": 0,
        "violations_count": answers.filter(time_violation=True).count(),
    }

    if answers.count() > 0:
        time_analysis["avg_time_per_question"] = (
            time_analysis["total_time"] / answers.count()
        )

    return {
        "attempt": attempt,
        "general": {
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "incorrect_answers": attempt.incorrect_answers,
            "accuracy": attempt.get_accuracy(),
            "status": attempt.get_status_display(),
            "s_index": attempt.s_index,
            "consistency": attempt.get_consistency_feedback_display(),
        },
        "level_analysis": attempt.level_analysis,
        "area_analysis": area_analysis,
        "time_analysis": time_analysis,
        "s_history": attempt.s_history,
    }


def export_attempt_to_csv(attempt: ExamAttempt) -> str:
    """
    Exporta los datos de un intento a formato CSV.

    Args:
        attempt: Instancia del intento

    Returns:
        String con contenido CSV
    """
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    output.write("\ufeff".encode("utf8").decode("utf8"))

    # Encabezados
    writer.writerow(
        [
            "#",
            "Nivel",
            "Área",
            "Tema de la Pregunta",
            "Respuesta Seleccionada",
            "Es Correcta",
            "Tiempo (s)",
            "Tiempo Permitido (s)",
            "Violación Tiempo",
            "Índice S",
        ]
    )

    # Datos
    for answer in attempt.answers.all().order_by("question_number"):
        writer.writerow(
            [
                answer.question_number,
                answer.difficulty_level.name if answer.difficulty_level else "N/A",
                (
                    answer.question.knowledge_area.name
                    if answer.question.knowledge_area
                    else "N/A"
                ),
                (answer.question.topic if answer.question.topic else "N/A"),
                (
                    answer.selected_option.option_text[:30] + "..."
                    if answer.selected_option.option_text
                    else "Respuesta no disponible"
                ),
                "Sí" if answer.is_correct else "No",
                answer.time_taken_seconds,
                answer.allowed_time_seconds,
                "Sí" if answer.time_violation else "No",
                round(answer.s_index_after, 4),
            ]
        )

    return output.getvalue()
