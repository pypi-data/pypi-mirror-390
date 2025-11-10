from django.urls import path
from purchase.api.views import (
VendorListCreate, ItemListCreate,
PurchaseBillCreatePost, VendorCreditCreatePost,
PaymentCreatePost, SupplierRefundCreatePost,
)


urlpatterns = [
    path("vendors/", VendorListCreate.as_view()),
    path("items/", ItemListCreate.as_view()),
    path("bills/", PurchaseBillCreatePost.as_view()),
    path("vendor-credits/", VendorCreditCreatePost.as_view()),
    path("payments/", PaymentCreatePost.as_view()),
    path("supplier-refunds/", SupplierRefundCreatePost.as_view()),
]