from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import *
urlpatterns = [
    path('user/create/', UserCreate.as_view(), name="create_user"),
    path('token/obtain/', ObtainTokenPair.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),


    path('rating/create/', Rating.as_view(), name='create_rating'),
    path('teammember/create/', TeamMember.as_view(), name='create_teammember'),
    path('subgroup/', SubGroups.as_view(), name='create_subgroup'),
    path('group/', Groups.as_view(), name='create_group'),
]
