from django.urls import path
from authera.views import OptionsView
from authera.views import ValidateScenarioView
from authera.views import RefreshTokenView

urlpatterns = [
    path("options/", OptionsView.as_view(), name='authera-options'),
    path("validate/<str:scenario_key>", ValidateScenarioView.as_view(), name='authera-validate'),
    path("refresh/", RefreshTokenView.as_view(), name='authera-refresh'),
]