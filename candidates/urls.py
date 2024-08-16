from django.urls import path
from .views import (initial_update_candidates, Final_update_candidates, 
                    CandidateDtailsUpdate, candidate_csv_download)

from .views import (FileFieldFormView, 
                    CandidateUpdateView,
                    CandidateDeleteView,
                    CandidateCreateView,
                    CandidateListView,
                    CandidateDetailView,
                    FinalCandidateUpdateView,
                    JobOfferCreateView,
                    JobOfferUpdateView,
                    OfferDeleteview,
                    CandidateDetailsListView, 
                    final_FileFieldFormView, 
                    OfferListView
                    )

app_name = 'candidates'

urlpatterns = [
    path('upload/<int:pk>', FileFieldFormView.as_view(), name='upload_candidate_files' ),
    path('final_upload/<int:pk>', final_FileFieldFormView.as_view(), name='final_upload_candidate_files' ),
    path('candidate/<int:pk>/new', CandidateCreateView.as_view(), name='candidate_new'),
    path('candidate/', CandidateListView.as_view(), name='candidates'),
    path('candidate/<int:pk>/update', CandidateUpdateView.as_view(), name='candidate_update'),
    path('finalcandidate/<int:pk>/update', FinalCandidateUpdateView.as_view(), name='final_candidate_update'),
    path('candidate/<int:pk>/delete', CandidateDeleteView.as_view(), name='candidate_delete'),
    path('candidate/<int:pk>/detail', CandidateDetailView.as_view(), name='candidate-detail'),
    path('candidate/<int:pk>/offer', JobOfferCreateView.as_view(), name='candidate-offer'),
    path('offer/<int:pk>/update', JobOfferUpdateView.as_view(), name='offer-update'),
    path('offer/<int:pk>/delete', OfferDeleteview.as_view(), name='offer-delete'),
    path('interview/<int:pk>/candidates/update/', initial_update_candidates, name='initial_canidadates_update'),
    path('final/<int:pk>/candidates/update/', Final_update_candidates, name='final_canidadates_update'),
    path('update-candidate-details/',CandidateDtailsUpdate , name='update_candidate_details'),
    path('candidate_details/', CandidateDetailsListView.as_view(), name='candidates_details'),
    path('candidate_details_csv/', candidate_csv_download, name='candidates_details_csv'),
    path('offer-list/', OfferListView.as_view(), name='offer-list'),
]
