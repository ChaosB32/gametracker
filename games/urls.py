from django.urls import path
from . import views

urlpatterns = [
    # Core
    path('', views.dashboard, name='dashboard'),
    path('jogos/', views.game_list, name='game_list'),
    path('jogos/novo/', views.game_create, name='game_create'),
    path('jogos/<int:pk>/', views.game_detail, name='game_detail'),
    path('jogos/<int:pk>/editar/', views.game_edit, name='game_edit'),
    path('jogos/<int:pk>/deletar/', views.game_delete, name='game_delete'),
    path('jogos/<int:pk>/insights/', views.generate_insights, name='generate_insights'),
    path('jogos/<int:pk>/favoritar/', views.toggle_favorite, name='toggle_favorite'),
    # Perfil
    path('perfil/', views.my_profile, name='my_profile'),
    path('perfil/<str:username>/', views.user_profile, name='user_profile'),
    # Social
    path('amigos/', views.friends_list, name='friends_list'),
    path('amigos/adicionar/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('amigos/aceitar/<str:username>/', views.accept_friend, name='accept_friend'),
    path('amigos/remover/<str:username>/', views.remove_friend, name='remove_friend'),
    path('amigos/comparar/<str:username>/', views.compare_with, name='compare_with'),
    # Auth
    path('auth/register/', views.register_view, name='register'),
    # API
    path('api/rawg/search/', views.rawg_search, name='rawg_search'),
    path('api/rawg/details/', views.rawg_details, name='rawg_details'),
    path('api/cache/stats/', views.cache_stats, name='cache_stats'),
    # Export
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
