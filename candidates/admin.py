from django.contrib import admin
from .models import Candidate, Offer, CandidatesDetails

# Register your models here.
admin.site.register(Candidate)
admin.site.register(Offer)
admin.site.register(CandidatesDetails)