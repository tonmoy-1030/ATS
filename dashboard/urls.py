from django.urls import path
from .views import DashBoard, SeparatedEMPJsonView

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', DashBoard.as_view(), name="dashboard"),
    path('separatedEMPjson/', SeparatedEMPJsonView.as_view(), name='separated_employee_json')

   
]
