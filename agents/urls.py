from django.urls import path

from . import views


app_name = "agents"


urlpatterns = [
    path(
    "<int:agent_id>/provider/<int:provider_id>/run-ai/",
    views.run_ai_analysis,
    name="run_ai_analysis",
    ),
    path(
        "",
        views.agent_list,
        name="agent_list",
    ),
    path(
        "create/",
        views.agent_create,
        name="agent_create",
    ),
    path(
        "<int:agent_id>/",
        views.agent_detail,
        name="agent_detail",
    ),
    path(
        "<int:agent_id>/edit/",
        views.agent_edit,
        name="agent_edit",
    ),
    path(
        "<int:agent_id>/delete/",
        views.agent_delete,
        name="agent_delete",
    ),
]