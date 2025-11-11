import operator
from functools import reduce
from rest_framework import viewsets
from rest_framework.views import APIView

from django.db.models.query_utils import Q

from models.category import Category
from serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        query = Q()

        if self.action == "list":
            query_params = self.request.query_params

            name = str(query_params.get("name", "")).split(" ")

            if name != "":
                query &= reduce(
                    operator.__and__,
                    (Q(name__unaccent__icontains=word) for word in name),
                )

            deactivates = query_params.get("deactivate", "").lower() == "true"

            query &= Q(deactivate=deactivates)

        return queryset.filter(query).order_by("name")