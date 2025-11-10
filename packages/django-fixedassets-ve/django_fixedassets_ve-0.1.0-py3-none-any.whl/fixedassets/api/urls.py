from django.urls import path
from fixedassets.api.views import (
    AssetCreate, AcquisitionCreatePost, RevaluationCreatePost, ImpairmentCreatePost, DisposalCreatePost, DepreciationPost,
)

urlpatterns = [
    path("assets/", AssetCreate.as_view()),
    path("acquisitions/", AcquisitionCreatePost.as_view()),
    path("revaluations/", RevaluationCreatePost.as_view()),
    path("impairments/", ImpairmentCreatePost.as_view()),
    path("disposals/", DisposalCreatePost.as_view()),
    path("depreciations/", DepreciationPost.as_view()),
]