from sales.models.doc_creditnote import CreditNoteLine


class CreditNoteLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNoteLine
        fields = ["item", "description", "qty", "rate", "discount", "tax"]


class CreditNoteCreateSerializer(serializers.ModelSerializer):
    lines = CreditNoteLineSerializer(many=True)
    class Meta:
        model = CreditNote
        fields = ["company", "customer", "number", "date", "currency", "invoice", "memo", "lines"]
        def create(self, validated_data):
            lines = validated_data.pop("lines", [])
            cn = CreditNote.objects.create(**validated_data)
            for l in lines:
                line = CreditNoteLine.objects.create(creditnote=cn, **l)
                line.recompute(False); line.save(update_fields=["net_amount", "tax_amount"])
                cn.recompute(); cn.save(update_fields=["subtotal", "tax_total", "grand_total"])
            return cn


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ["company", "customer", "date", "currency", "amount", "via", "memo"]