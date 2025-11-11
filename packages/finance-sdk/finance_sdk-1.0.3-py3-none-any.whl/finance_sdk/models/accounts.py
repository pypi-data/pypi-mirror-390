from django.db import models

from models import bank

class Account(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    bank = models.ForeignKey(bank, on_delete=models.PROTECT)
    deactivate = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField()

    def __str__(self):
        return self.name + " - " + self.bank.name


class AccountPermission(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    employee = models.JSONField()
    deactivate = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_app = models.JSONField()

    def __str__(self):
        return "Account: %s | %s" % (self.account, self.employee)

    @staticmethod
    def get_account(user_id, client_app):
        accounts = Account.objects.filter(
            id__in=[
                AccountPermission.objects.filter(
                    employee__user_id=user_id,
                    client_app_id=client_app,
                    deactivate=False,
                    account__bank__deactivate=False,
                ).values_list("account_id")
            ]
        )

        return accounts