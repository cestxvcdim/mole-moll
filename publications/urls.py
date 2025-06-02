from django.urls import path

from publications.apps import PublicationsConfig
from publications import views

app_name = PublicationsConfig.name


urlpatterns = [
    path('', views.PublicationListView.as_view(), name='publication-list'),
    path('<int:pk>/', views.PublicationDetailView.as_view(), name='publication-detail'),
    path('create/', views.PublicationCreateView.as_view(), name='publication-create'),
    path('<int:pk>/update/', views.PublicationUpdateView.as_view(), name='publication-update'),
    path('<int:pk>/delete/', views.PublicationDeleteView.as_view(), name='publication-delete'),

    path('comment/<int:pk>/add-comment/', views.add_comment, name='add-commentary'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit-commentary'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete-commentary'),

    path('<int:pk>/like/', views.toggle_publication_like, name='toggle-publication-like'),
    path('comment/<int:pk>/like/', views.toggle_comment_like, name='toggle-comment-like'),
]
