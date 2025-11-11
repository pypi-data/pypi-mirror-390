from rest_framework import serializers
from models.payment import PaymentMethod, PaymentMethodTaxs


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name", "tax"]

    def validate_name(self, value):
        if not (self.instance and value == self.instance.name):
            if PaymentMethod.objects.filter(
                name=value, deactivate=False, client_app=self.initial_data.get('client_app')).exists():
                raise serializers.ValidationError(
                    "Already exists a payment method with this name."
                )

        return value

    def validate_tax(self, value):
        if  value is not None and value < 0:
            raise serializers.ValidationError("the tax can't be negative")

        return value


class PaymentMethodTaxsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodTaxs
        fields = ["id", "initial_payment", "final_payment", "tax"]

    def validate(self, attrs):
        if attrs["initial_payment"] > attrs["final_payment"]:
            raise serializers.ValidationError(
                {"menssage": " The initial payment can't be bigger then the final_payment"}
            )

        taxs = PaymentMethodTaxs.objects.filter(
            payment_method_id=self.context.get("payment_method_id"),
            client_app=self.initial_data.get('client_app'),
        )

        if self.instance:
            taxs = taxs.exclude(id=self.instance.id)

        for tax in taxs:
            if attrs["initial_payment"] in range(
                tax.initial_payment, tax.final_payment + 1
            ):
                raise serializers.ValidationError(
                    {
                        "initial_payment": "Already exists a tax for this payment in this payment method."
                    }
                )
            elif attrs["final_payment"] in range(
                tax.initial_payment, tax.final_payment + 1
            ):
                raise serializers.ValidationError(
                    {
                        "final_payment": "Already exists a tax for this payment in this payment method."
                    }
                )
            elif (
                tax.initial_payment >= attrs["initial_payment"]
                and tax.final_payment <= attrs["final_payment"]
            ):
                raise serializers.ValidationError(
                    {
                        "menssage": "Already exists a tax for this payments in this payment method."
                    }
                )

        return attrs