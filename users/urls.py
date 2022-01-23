from django.urls import path
from . import views

urlpatterns = [
  path('login/', views.loginUser, name='login'),
  path('logout/', views.logoutUser, name='logout'),
  path('register/', views.registerUser, name='register'),


  path('', views.profiles, name='profiles'),
  path('profile/<str:pk>/', views.userProfile, name='profile'),
  path('account/' , views.userAccount , name='user-account'),
  path('edit-account/', views.editAccount, name='edit-account'),

  path('inbox/', views.inbox , name='inbox'),
  path('message/<str:pk>', views.message , name='message'),
  path('create-message/<str:pk>', views.createMessage , name='create-message'),

  path('create-skill', views.createSkill, name='create-skill'),
  path('update-skill/<str:pk>', views.updateSkill, name='update-skill'),
  path('delete-skill/<str:pk>', views.deleteSkill, name='delete-skill'),
]