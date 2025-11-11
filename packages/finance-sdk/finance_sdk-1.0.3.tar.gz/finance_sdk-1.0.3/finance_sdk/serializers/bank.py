from rest_framework import serializers
from models.bank import Bank


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = ["id", "name"]

    def validate_name(self, value):
        if not (self.instance and value == self.instance.name):
            if Bank.objects.filter(
                name=value, deactivate =False, client_app=self.initial_data.get('client_app')
            ).exists():
                raise serializers.ValidationError(
                    "Already exists a bank with this name"
                )

        return value
