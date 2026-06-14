from django.urls import path
from . import views

urlpatterns = [
    # Home / upload
    path('', views.HomeView.as_view(), name='home'),
    path('predict/', views.PredictView.as_view(), name='predict'),

    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Dashboard & history
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('history/', views.HistoryView.as_view(), name='history'),

    # Image detail & management
    path('image/<int:pk>/', views.ImageDetailView.as_view(), name='image_detail'),
    path('image/<int:pk>/delete/', views.ImageDeleteView.as_view(), name='image_delete'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Downloads
    path('download/<path:relative_path>/', views.DownloadImageView.as_view(), name='download_image'),
    path('download/saved/<int:pk>/', views.DownloadSavedImageView.as_view(), name='download_saved'),
]
