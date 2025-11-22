from django.db import models


class AcademicLevel(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_academic_levels"

    def __str__(self):
        return self.name


class AcademicDepartment(models.Model):
    name = models.CharField(max_length=150)
    modality = models.ForeignKey(
        "app.Modality",
        on_delete=models.CASCADE,
        related_name="academic_departments",
        null=True,
        blank=True,
    )

    academic_level = models.ForeignKey(
        AcademicLevel,
        on_delete=models.CASCADE,
        related_name="academic_departments",
        null=True,
        blank=True,
    )

    representative = models.ForeignKey(
        "app.Representative",
        on_delete=models.CASCADE,
        related_name="academic_departments",
        null=True,
        blank=True,
    )

    institution = models.ForeignKey(
        "app.Institution", on_delete=models.CASCADE, related_name="academic_departments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_academic_departments"

    def __str__(self):
        return self.name
