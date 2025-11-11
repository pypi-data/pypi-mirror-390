from django.db import models

from category import Category
from payment import PaymentMethod
from accounts import Account

from enums import Frequency, Type, RegistryClassification

class Entry(models.Model):
    due_date = models.DateField(blank=False)
    payment_date = models.DateField(blank=True, null=True)
    description = models.TextField("Description", blank=False)
    category = models.ForeignKey(
        Category,
        verbose_name="Category",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    value = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False)
    received_value = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    liquid_value = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, null=True
    )
    registry_classification = models.CharField(
        max_length=30,
        blank=True,
        null=False,
        default=RegistryClassification.VARIABLE,
        choices=RegistryClassification.CHOICES,
    )
    number_of_payments = models.PositiveIntegerField(default=1, null=False, blank=False)
    current_payment = models.PositiveIntegerField(default=1, null=False, blank=False)
    frequency = models.IntegerField(
        choices=Frequency, default=Frequency.NONE, null=True, blank=True
    )
    reference_record = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=False, related_name="payments"
    )
    observation = models.TextField(blank=True, null=True)
    cost_center = models.JSONField(default=dict)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, blank=True, null=True)
    entry_type = models.CharField(max_length=1, choices=Type.CHOICES, blank=False)
    person = models.JSONField(default=dict)
    tag = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField(default=dict, null=False, blank=False)
