from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('update-task/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('save-session', views.save_session, name='save_session'),
    path('api/bitcoin-price/', views.bitcoin_price_api, name='bitcoin_price_api'),
]