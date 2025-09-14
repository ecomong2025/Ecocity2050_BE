from django.urls import path
from . import views

urlpatterns = [
    path('save-game/', views.save_game_data, name='save_game_data'),
    path('load-game/', views.load_game_data, name='load_game_data'),
    path('check-saved-data/', views.check_saved_data_exists, name='check_saved_data_exists'),
]