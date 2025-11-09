from django.urls import path
from finacc.api.views import AccountListCreate, JournalEntryCreatePost, TrialBalanceView


urlpatterns = [
    path("accounts/", AccountListCreate.as_view()),
    path("journal/entries/", JournalEntryCreatePost.as_view()),
    path("reports/trial-balance/", TrialBalanceView.as_view()),
]