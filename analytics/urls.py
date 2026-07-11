from django.urls import path

from . import views


app_name = "analytics"


urlpatterns = [
    path(
        "forecasts/",
        views.forecast_dashboard,
        name="forecast_dashboard",
    ),
    path(
        "forecasts/run/<int:agent_id>/",
        views.run_agent_forecast,
        name="run_agent_forecast",
    ),
    path(
        "anomalies/",
        views.anomaly_review,
        name="anomaly_review",
    ),
    path(
        "metrics/",
        views.metrics_dashboard,
        name="metrics_dashboard",
    ),
    path(
        "data-quality/",
        views.data_quality_dashboard,
        name="data_quality",
    ),
]