from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from purchase.api.serializers import (
VendorSerializer, ItemSerializer,
PurchaseBillCreateSerializer, VendorCreditCreateSerializer,
PaymentSerializer, SupplierRefundSerializer,
)
from purchase.posting.adapters import (
post_purchase_bill, post_vendor_credit, post_payment, post_supplier_refund,
)
from purchase.conf import get as confget


class VendorListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = VendorSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ItemListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = ItemSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class PurchaseBillCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = PurchaseBillCreateSerializer(data=request.data); ser.is_valid(raise_exception=True)
        bill = ser.save()
        if confget("AUTO_POST_BILL"):
            entry = post_purchase_bill(bill)
            return Response({"bill_id": bill.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"bill_id": bill.id}, status=status.HTTP_201_CREATED)


class VendorCreditCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = VendorCreditCreateSerializer(data=request.data); ser.is_valid(raise_exception=True)
        vc = ser.save()
        if confget("AUTO_POST_VENDORCREDIT"):
            entry = post_vendor_credit(vc)
            return Response({"vendor_credit_id": vc.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"vendor_credit_id": vc.id}, status=status.HTTP_201_CREATED)


class PaymentCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = PaymentSerializer(data=request.data); ser.is_valid(raise_exception=True)
        pmt = ser.save()
        if confget("AUTO_POST_PAYMENT"):
            entry = post_payment(pmt)
            return Response({"payment_id": pmt.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"payment_id": pmt.id}, status=status.HTTP_201_CREATED)


class SupplierRefundCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = SupplierRefundSerializer(data=request.data); ser.is_valid(raise_exception=True)
        ref = ser.save()
        if confget("AUTO_POST_SUPPLIER_REFUND"):
            entry = post_supplier_refund(ref)
            return Response({"supplier_refund_id": ref.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"supplier_refund_id": ref.id}, status=status.HTTP_201_CREATED)