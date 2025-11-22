from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=150)
    tax_id = models.CharField(max_length=30, unique=True)
    principal = models.ForeignKey(
        "app.Principal", on_delete=models.CASCADE, related_name="institutions"
    )

    institution_type = models.ForeignKey(
        "app.InstitutionType", on_delete=models.CASCADE, related_name="institutions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_institutions"

    def __str__(self):
        return self.name
