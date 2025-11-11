import operator
from functools import reduce
from rest_framework import viewsets
from rest_framework.views import APIView

from django.db.models.query_utils import Q

from models.bank import Bank
from serializers.bank import BankSerializer

class BankViewSet(viewsets.ModelViewSet):

    serializer_class = BankSerializer
    queryset = Bank.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        query = Q(deactivate=False)

        if self.action == "list":
            name = str(self.request.query_params.get("name", "")).split(" ")

            if name != "":
                query &= reduce(
                    operator.__and__,
                    (Q(name__unaccent__icontains=word) for word in name),
                )

        return queryset.filter(query).order_by("-name")
