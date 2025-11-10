from django.urls import path
from sales.api.views import (
CustomerListCreate, ItemListCreate, SalesInvoiceCreatePost, ReceiptCreatePost,
CreditNoteCreatePost, RefundCreatePost,
)


urlpatterns = [
    path("customers/", CustomerListCreate.as_view()),
    path("items/", ItemListCreate.as_view()),
    path("invoices/", SalesInvoiceCreatePost.as_view()),
    path("credit-notes/", CreditNoteCreatePost.as_view()),
    path("receipts/", ReceiptCreatePost.as_view()),
    path("refunds/", RefundCreatePost.as_view()),
]