from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, F
from finacc.api.serializers import AccountSerializer, JournalEntryCreateSerializer
from finacc.models.accounts import Account
from finacc.models.journal import JournalLine
from finacc.posting.engine import post_entry
from finacc.conf import get as confget


class AccountListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]


def get(self, request):
    company = request.query_params.get("company")
    qs = Account.objects.filter(company_id=company)
    return Response(AccountSerializer(qs, many=True).data)


def post(self, request):
    ser = AccountSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data, status=status.HTTP_201_CREATED)


class JournalEntryCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]


def post(self, request):
    ser = JournalEntryCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    entry = ser.save()
    if confget("AUTO_POST_ON_CREATE"):
         entry = post_entry(entry)
    return Response({"id": entry.id, "posted": entry.is_posted}, status=status.HTTP_201_CREATED)


class TrialBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]


def get(self, request):
    company = request.query_params["company"]
    date_to = request.query_params["to"]
    qs = (
    JournalLine.objects
    .filter(entry__company_id=company, entry__is_posted=True, entry__date__lte=date_to)
    .values("account_id", code=F("account__code"), name=F("account__name"))
    .annotate(dr=Sum("debit"), cr=Sum("credit"))
    .order_by("code")
    )
    return Response(list(qs))