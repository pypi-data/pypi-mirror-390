from django.db import models

class PaymentMethod(models.Model):
    name = models.CharField("Nome", max_length=200, blank=False, null=False)
    tax = models.DecimalField(
        decimal_places=2, max_digits=9, blank=True, null=True, default=0
    )
    deactivate = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField()


    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.taxa == "":
            self.taxa = 0

        super(PaymentMethod, self).save(*args, **kwargs)


class PaymentMethodTaxs(models.Model):
    initial_payment = models.PositiveIntegerField()
    final_payment = models.PositiveIntegerField()
    tax = models.DecimalField(decimal_places=2, max_digits=5)
    PaymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    client_app = models.JSONField()
