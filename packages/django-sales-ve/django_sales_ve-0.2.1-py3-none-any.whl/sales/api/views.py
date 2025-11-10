class CreditNoteCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = CreditNoteCreateSerializer(data=request.data); ser.is_valid(raise_exception=True)
        cn = ser.save()
        from sales.conf import get as confget
            if confget("AUTO_POST_CREDITNOTE"):
                entry = post_credit_note(cn)
            return Response({"credit_note_id": cn.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"credit_note_id": cn.id}, status=status.HTTP_201_CREATED)


class RefundCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = RefundSerializer(data=request.data); ser.is_valid(raise_exception=True)
        ref = ser.save()
        from sales.conf import get as confget
        if confget("AUTO_POST_REFUND"):
            entry = post_refund(ref)
            return Response({"refund_id": ref.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"refund_id": ref.id}, status=status.HTTP_201_CREATED)