import operator
from functools import reduce
from rest_framework import viewsets
from rest_framework.views import APIView

from django.db.models.query_utils import Q

from models.accounts import Account, AccountPermission
from serializers.accounts import AccountSerializer, AccountPermissionSerializer



class AccountViewSet(viewsets.ModelViewSet):

    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()

        query = Q(deactivate=False)

        if self.action == "list":
            LIST = "list"
            INDICATORS = "indicators"

            name = str(self.request.query_params.get("name", ""))

            use = self.validate_item_in_list(
                item=self.request.query_params.get("use", "list"),
                list=[LIST, INDICATORS],
                message="Invalid",
                required=True,
            )

            if use == INDICATORS:
                queryset = AccountPermission.get_conta(
                    self.request.user.id, self.request.META["HTTP_CLIENTE_APP_ID"]
                )

            if name != "":
                query &= reduce(
                    operator.__and__,
                    (
                        Q(name__unaccent__icontains=word)
                        for word in name.split(" ")
                    ),
                )

        return queryset.filter(query).order_by("name")