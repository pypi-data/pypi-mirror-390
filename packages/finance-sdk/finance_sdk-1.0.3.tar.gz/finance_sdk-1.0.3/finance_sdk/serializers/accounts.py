from rest_framework import serializers
from models.accounts import Account, AccountPermission


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "bank"]

    def validate_name(self, value):
        if not (self.instance and value == self.instance.name):
            if Account.objects.filter(
                name=value, deactivate=False, client_app=self.initial_data.get('client_app')).exists():
                raise serializers.ValidationError(
                    "Already exists an account with this name."
                )

        return value
    


class AccountPermissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccountPermission
        fields = ["id", "account", "employee"]
        validators = []

    def validate(self, attrs):
        if (
            AccountPermission.objects.filter(
                employee__id=attrs["employee"],
                account=attrs["account"],
                deactivate=False,
                account__deactivate=False,
                account__bank__deactivate=False,
            ).exists()
        ):
            raise serializers.ValidationError(
                {"employee": "This employee already has permission"}
            )

        return attrs
    

