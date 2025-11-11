from datetime import date, timedelta
from finance_sdk.models.entry import Entry


from enums import Frequency

def generate_entries(validated_data, initial_data):
    number_of_payments = validated_data.get("number_of_payments", 1)
    payment_value = validated_data.get("value") / number_of_payments
    frequency = validated_data.get("frequency")
    validated_data["frequency"] = Frequency.get_frequency(frequency=frequency)
    primary_payment = Entry.objects.create(**validated_data)
    payment_method = primary_payment.payment_method
    tax = payment_method.tax / 100 if payment_method else 0
    liquid_value = (
            payment_value - payment_value * tax
            if validated_data.get("type") == Entry.entry_type.ENTRY
            else None
        )
    primary_payment.value = payment_value
    primary_payment.liquid_value = liquid_value
    primary_payment.client_app = initial_data.get('client_app')
    primary_payment.reference_record_id = primary_payment.id
    primary_payment.save()

    if number_of_payments > 1:
            entry_payments = []
            for payment in range(2, number_of_payments + 1):
                entry_payments.append(
                    Entry(
                        description=validated_data.get("description"),
                        value=payment_value,
                        liquid_value=liquid_value,
                        category=validated_data.get("category"),
                        account=validated_data.get("account"),
                        cost_center=validated_data.get("cost_center"),
                        due_date=validated_data.get("due_date")
                        + timedelta(days=frequency * (payment - 1)),
                        payment_method=validated_data.get("payment_method"),
                        person=validated_data.get("person"),
                        entry_type=validated_data.get("entry_type"),
                        registry_classification=validated_data.get(
                            "registry_classification"
                        ),
                        number_of_payments=validated_data.get("number_of_payments"),
                        current_payment=payment,
                        frequency=primary_payment.frequency,
                        reference_record_id=primary_payment.pk,
                        client_app=initial_data.get('client_app'),
                    )
                )

            Entry.objects.bulk_create(entry_payments)
    else:
        received_value = validated_data.get("received_value", 0)
        total_value = validated_data.get("value", 0)

            
    if received_value < total_value and received_value > 0:
                Entry.objects.create(
                    description=validated_data.get("description"),
                    value=total_value - received_value,
                    category=validated_data.get("category"),
                    account=validated_data.get("account"),
                    cost_center=validated_data.get("cost_center"),
                    due_date=validated_data.get("due_date"),
                    person=validated_data.get("person"),
                    entry_type=validated_data.get("entry_type"),
                    registry_classification=validated_data.get("registry_classification"),
                    number_of_payments=validated_data.get("numero_parcelas", 1),
                    cliente_app_id=initial_data.get('client_app'),
                )

    return primary_payment
    


