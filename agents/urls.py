from django.urls import path

from . import views


app_name = "agents"


urlpatterns = [
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