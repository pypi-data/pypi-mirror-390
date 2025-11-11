from argparse import Action
import operator
from functools import reduce
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView

from django.db.models.query_utils import Q
from finance_sdk_wlc.finance_sdk.utils import validate_item_in_list, validate_natural_number

from enums import Frequency, Type

from models.entry import Entry
from serializers.entry import EntrySerializer

from models.accounts import Account, AccountPermission


class EntryViewSet( viewsets.ModelViewSet):

    serializer_class = EntrySerializer
    queryset = Entry.objects.all()
    

    def get_queryset(self):
        client_app_id = self.request.query_params.get("client_app")
        employee_id = self.request.query_params.get("employee")

        queryset = self.queryset

        query = (
            (
                Q(
                    account_id__in=AccountPermission.get_conta(
                        self.request.user.id, client_app_id
                    ),
                    account__deactivate=False,
                    account__bank__deactivate=False,
                )
                    | Q(account__isnull=True) )
            & 

             (
               Q(payment_method__isnull=False, payment_method__desativada=False)
                | Q(payment_method__isnull=True)
            )
            & (
                Q(category__isnull=False, category__deactivate=False)
                | Q(category__isnull=True)
            )

            (
                Q(person_isnull=False) | Q(person_isnull=True)
            )
        )

        person_id = self.request.query_params.getlist("person_ids", [])

        if person_id:
            query &= Q(person__id__in=person_id)

        if client_app_id:
            query &= Q(client_app__id=client_app_id)

        cost_center_id = self.request.query_params.getlist("cost_center", [])
        
        if cost_center_id:
            query &= Q(cost_center__id__in=cost_center_id)


        if self.action == "list":
            query_params = self.request.query_params

            entry_type = self.validate_item_in_list(
                item=query_params.get("tipo", False),
                lista=dict(Entry.Type.TYPE).keys(),
                message="Entry type invalid",
                message_if_empty="Entry type required",
                required=True,
            )

            initial_date, final_date = self.validar_periodo_datas(
                initial_date=query_params.get("initial_date", False),
                final_date=query_params.get("final_date", False),
            )

            query &= Q(
                entry_type=entry_type, due_date__gte=initial_date, due_date__lte=final_date
            )

            cost_center = validate_natural_number(
                numero=query_params.get("cost_center", False),
                mensagem="Invalid Cost Center",
            )

            if cost_center:
                query &= Q(cost_center_id=cost_center)

            person = query_params.get("person", False)

            if person:
                person = person.split(" ")
                query &= reduce(
                    operator.__and__,
                    (Q(person__name__unaccent__icontains=param) for param in person),
                )

            category = validate_natural_number(
                number=query_params.get("category", False),
                message="Inválid Category",
            )

            if category:
                query &= Q(categoria_id=category)

            account = validate_natural_number(
                number=query_params.get("account", False), message="Invalid Account"
            )

            if account:
                query &= Q(account_id=account)

        return queryset.filter(query).order_by(
            "due_date", "category", "description", "created_at", "id"
        )

    def list(self, request, *args, **kwargs):
        if "values" not in request.query_params:
            return super().list(request, *args, **kwargs)
 
        serializer_data = EntrySerializer(
            {"Entry": self.get_queryset()}, context={"request": request}
        ).data

        return Response(data=serializer_data["valores"])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        recalculate_liquid_value = request.data.get("recalculate", False)
        serializer = EntrySerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request, "recalculate": recalculate_liquid_value},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if Entry.objects.filter(reference_record=instance).count() > 1:
            return Response(
                {"message": "Payment deletion requires confirmation."},
                ),
              

        instance.reference_record = None
        instance.save()

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @Action(methods=["GET"], detail=True, url_path="payments")
    def list_payments(self, request, pk=None):
        entry = self.get_object()

        if entry.reference_record:
            payments = Entry.objects.filter(
                reference_record=entry.reference_record
            ).order_by("id")
        else:
            payments = Entry.objects.filter(id=entry.id)

        
        page = self.paginate_queryset(payments)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

        

    @Action(methods=["DELETE"], detail=True, url_path="confirm_payment")
    def confirm_payment_deletion(self, request, pk=None):
        entry = self.get_object()

        payments = Entry.objects.filter(reference_record=entry).exclude(
            pk=entry.pk
        )

        for payment in payments:
            self.perform_destroy(payment)

        entry.reference_record = None
        entry.save()

        self.perform_destroy(entry)

        return Response()