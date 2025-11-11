from rest_framework import serializers
from models.category import Category

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "principal_category",
            "is_entry",
            "is_out",
            "deactivate",
        ]

    def validate_name(self, value):
        if not (self.instance and value == self.instance.name):
            if Category.objects.filter(
                name=value, deactivate=False, client_app=self.initial_data.get('client_app')).exists():
                raise serializers.ValidationError(
                    "Already exists a category with this name."
                )

            if Category.objects.filter(
                name=value, deactivate=True, client_app=self.initial_data.get('client_app')).exists():
                raise serializers.ValidationError(
                    "Already exists a category with this name."
                )

        return value