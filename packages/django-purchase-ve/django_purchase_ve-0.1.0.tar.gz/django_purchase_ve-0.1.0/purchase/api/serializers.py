from purchase.models.doc_bill import PurchaseBill, PurchaseBillLine
from purchase.models.doc_payment import Payment, SupplierRefund
from purchase.models.doc_vendorcredit import VendorCredit, VendorCreditLine
from purchase.models.item import Item
from purchase.models.party import Vendor
from rest_framework import serializers
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"

class PurchaseBillLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseBillLine
        fields = ["item", "description", "qty", "rate", "discount", "tax"]


class PurchaseBillCreateSerializer(serializers.ModelSerializer):
    lines = PurchaseBillLineSerializer(many=True)
    class Meta:
        model = PurchaseBill
        fields = ["company", "vendor", "number", "date", "currency", "is_tax_inclusive", "memo", "lines"]
        def create(self, validated_data):
            lines = validated_data.pop("lines", [])
            bill = PurchaseBill.objects.create(**validated_data)
            for l in lines:
                line = PurchaseBillLine.objects.create(bill=bill, **l)
            line.recompute(bill.is_tax_inclusive); line.save(update_fields=["net_amount", "tax_amount"])
            bill.recompute(); bill.save(update_fields=["subtotal", "tax_total", "grand_total"])
            return bill


class VendorCreditLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCreditLine
        fields = ["item", "description", "qty", "rate", "discount", "tax"]


class VendorCreditCreateSerializer(serializers.ModelSerializer):
    lines = VendorCreditLineSerializer(many=True)
    class Meta:
        model = VendorCredit
        fields = ["company", "vendor", "number", "date", "currency", "bill", "memo", "lines"]
        def create(self, validated_data):
            lines = validated_data.pop("lines", [])
            vc = VendorCredit.objects.create(**validated_data)
            for l in lines:
                line = VendorCreditLine.objects.create(vendorcredit=vc, **l)
                line.recompute(False); line.save(update_fields=["net_amount", "tax_amount"])
                vc.recompute(); vc.save(update_fields=["subtotal", "tax_total", "grand_total"])
                return vc


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["company", "vendor", "date", "currency", "amount", "via", "memo"]


class SupplierRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRefund
        fields = ["company", "vendor", "date", "currency", "amount", "via", "memo"]