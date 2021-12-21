from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import *
urlpatterns = [
    path('user/create/', UserCreate.as_view(), name="create_user"),
    path('token/obtain/', ObtainTokenPair.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('blacklist/', LogoutAndBlacklistRefreshTokenForUserView.as_view(),
         name='blacklist'),


    path('rating/create/', Rating.as_view(), name='create_rating'),
    path('teammember/create/', TeamMembers.as_view(), name='create_teammember'),
    path('subgroup/', SubGroups.as_view(), name='create_subgroup'),
    # path('subgroup/team/', Teams.as_view(), name='create_team'),
    path('group/', Groups.as_view(), name='create_group'),
    path('subgroup/students/', GroupStudent.as_view(), name='get_group_studetns'),
    path('subgroup/teammembers/', TeamMembers.as_view(), name='get_teammembers'),
    path('subgroup/teammembers/scores/',
         GroupRatings.as_view(), name='get_teammembers'),


    path('home/', GroupStudentGetStudent.as_view(), name='get_groups'),
    path('home/myteam/', MyTeam.as_view(), name='get_groups'),
    path('rating-criterias/', RatingCriterias.as_view(), name='get_rc'),


]
