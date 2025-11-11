from django.db import transaction
from datetime import date, timedelta

from rest_framework import serializers
from finance_sdk.models.entry import Entry
from finance_sdk.models.accounts import AccountPermission

from enums import Frequency, Type, RegistryClassification
from services.entriesService import generate_entries

class EntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entry
        fields = [
            "id",
            "description",
            "value",
            "received_value",
            "liquid_value",
            "category",
            "account",
            "cost_center",
            "payment_date",
            "due_date",
            "payment_method",
            "person",
            "entry_type",
            "registry_classification",
            "tag",
            "number_of_payments",
            "current_payment",
            "frequency", 
            "reference_record",
           
        ]

        read_only_fields = [
            "current_payment",
            "reference_record",
            "frequency",
            "liquid_value",
        ]

    @transaction.atomic
    def create(self, validated_data):
        return generate_entries(self.initial_data, validated_data)

    def update(self, instance, validated_data):
        validated_data["number_of_payments"] = instance.number_of_payments
        validated_data["frequency"] = instance.frequency
        validated_data["reference_record"] = instance.reference_record
        value = validated_data.get("value")
        entry_type = (
            validated_data.get("entry_type")
            if validated_data.get("entry_type") is not None
            else instance.entry_type
        )
        if value is not None and entry_type == Entry.entry_type.ENTRY:
            payment_method = (
                validated_data.get("payment_method")
                if validated_data.get("payment_method") is not None
                else instance.payment_method
            )
            if payment_method is not None:
                validated_data["liquid_value"] = value * (payment_method.tax / 100)

        if self.context.get("recalcular") and instance.forma_pagamento is not None:
            validated_data["valor_liquido"] = instance.valor * (
                instance.forma_pagamento.taxa / 100
            )

        return super().update(instance, validated_data)

    def validate_payment_date(self, value):
        DATE_LIMIT = date(2000, 1, 1)

        if DATE_LIMIT > value:
            raise serializers.ValidationError(
                "Date can't be lower then 2000-01-01"
            )

        return value

    def validate_due_date(self, value):
        DATE_LIMIT = date(2000, 1, 1)

        if DATE_LIMIT > value:
            raise serializers.ValidationError(
                "Date can't be lower then 2000-01-01"
            )
        return value

    def validate_value(self, value):
        if not value > 0:
            raise serializers.ValidationError("The value must be greater than 0")

        return value

    def validate_account(self, value):
        if not AccountPermission.objects.filter(
            account=value, employee_id=self.initial_data.get('employee')
        ).exists():
            raise serializers.ValidationError("Invalid Account")

        return value

    def validate_number_of_payments(self, value):
        if not value > 0:
            raise serializers.ValidationError(
                "Number of payments must be greater then 0"
            )

        return value

    
    def validate(self, attrs):
        frequency = attrs.get("frequency", Frequency.NONE)

        if (frequency == Frequency.NONE) and (attrs.get("number_of_payments", 1) > 1):
            raise serializers.ValidationError(
                {
                    "message": "An accounts payable/receivable entry without any recurrence cannot have more than one payment."
                } 
            )

        if (attrs.get("number_of_payments", 1) == 1) and (
            frequency != Frequency.NONE
        ):
            raise serializers.ValidationError(
                {
                    "message": "The number of payments must be greater than 1 in order to have a frequency."
                }  )

        value = attrs.get("value")
        entry_type = attrs.get("entry_type")
        if value and entry_type == Type.ENTRY:
            paid_value = attrs.get("paid_value", 0)
            if value < paid_value:
                raise serializers.ValidationError(
                    {"message": "The Paid value can't be greater than the value."}
                )

        return attrs