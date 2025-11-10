from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from fixedassets.api.serializers import *
from fixedassets.models.asset import Asset
from fixedassets.models.schedule import DepreciationLine
from fixedassets.posting.adapters import post_acquisition, post_revaluation, post_impairment, post_disposal, post_depreciation
from fixedassets.conf import get as confget

class AssetCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = AssetSerializer(data=request.data); ser.is_valid(raise_exception=True); obj = ser.save()
        return Response({"asset_id": obj.id}, status=status.HTTP_201_CREATED)

class AcquisitionCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = AcquisitionSerializer(data=request.data); ser.is_valid(raise_exception=True); acq = ser.save()
        if confget("AUTO_POST"): entry = post_acquisition(acq); return Response({"acquisition_id": acq.id, "journal_entry_id": entry.id}, status=201)
        return Response({"acquisition_id": acq.id}, status=201)

class RevaluationCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = RevaluationSerializer(data=request.data); ser.is_valid(raise_exception=True); rv = ser.save()
        if confget("AUTO_POST"): entry = post_revaluation(rv); return Response({"revaluation_id": rv.id, "journal_entry_id": getattr(entry, 'id', None)}, status=201)
        return Response({"revaluation_id": rv.id}, status=201)

class ImpairmentCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = ImpairmentSerializer(data=request.data); ser.is_valid(raise_exception=True); im = ser.save()
        if confget("AUTO_POST"): entry = post_impairment(im); return Response({"impairment_id": im.id, "journal_entry_id": entry.id}, status=201)
        return Response({"impairment_id": im.id}, status=201)

class DisposalCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = DisposalSerializer(data=request.data); ser.is_valid(raise_exception=True); ds = ser.save()
        if confget("AUTO_POST"): entry = post_disposal(ds); return Response({"disposal_id": ds.id, "journal_entry_id": entry.id}, status=201)
        return Response({"disposal_id": ds.id}, status=201)

class DepreciationPost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = DepreciationLineSerializer(data=request.data); ser.is_valid(raise_exception=True); dl = ser.save()
        if confget("AUTO_POST"): entry = post_depreciation(dl); return Response({"depr_line_id": dl.id, "journal_entry_id": entry.id}, status=201)
        return Response({"depr_line_id": dl.id}, status=201)