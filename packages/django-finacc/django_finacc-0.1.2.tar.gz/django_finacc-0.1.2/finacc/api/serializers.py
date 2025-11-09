from rest_framework import serializers
from finacc.models.accounts import Account
from finacc.models.journal import JournalEntry, JournalLine


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "company", "code", "name", "kind", "normal_balance", "parent", "is_leaf", "is_active"]


class JournalLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = ["account", "description", "debit", "credit"]


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True)


class Meta:
    model = JournalEntry
    fields = ["company", "date", "memo", "currency", "lines"]


def create(self, validated_data):
    lines = validated_data.pop("lines", [])
    entry = JournalEntry.objects.create(**validated_data)
    for l in lines:
        JournalLine.objects.create(entry=entry, **l)
        return entry