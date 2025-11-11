from django.db import models

class Category(models.Model):
    name = models.CharField("Nome", max_length=200, blank=False, null=False)
    principal_category = models.ForeignKey(
        "self", on_delete=models.PROTECT, blank=True, null=True
    )
    is_entry = models.BooleanField(default=True, blank=False, null=False)
    is_out = models.BooleanField(default=True, blank=False, null=False)
    deactivate = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField()


    def __str__(self):
        return self.name