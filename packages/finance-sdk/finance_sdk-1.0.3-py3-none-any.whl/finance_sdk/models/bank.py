from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    deactivate = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField()

    def __str__(self):
        return self.name
