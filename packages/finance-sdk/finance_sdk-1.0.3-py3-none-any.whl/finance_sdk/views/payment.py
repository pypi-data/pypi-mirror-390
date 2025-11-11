import operator
from functools import reduce
from rest_framework import viewsets
from rest_framework.views import APIView
from django.http.response import Http404, HttpResponse
from rest_framework.response import Response

from django.db.models.query_utils import Q

from models.payment import PaymentMethod, PaymentMethodTaxs
from serializers.payments import PaymentMethodSerializer, PaymentMethodTaxsSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentMethodSerializer
    queryset = PaymentMethod.objects.all()

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

        return queryset.filter(query).order_by("name")


class ListPaymentMethodTaxs(viewsets.ModelViewSet):

    serializer_class = PaymentMethodTaxsSerializer
    queryset = PaymentMethodTaxs.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()

        query = Q(deactivate=False)

        if self.action == "list":
            tax = str(self.request.query_params.get("tax", "")).split(" ")

            if tax != "":
                query &= reduce(
                    operator.__and__,
                    (Q(tax__icontains=word) for word in tax),
                )

        return queryset.filter(query).order_by("initial_date")
    
