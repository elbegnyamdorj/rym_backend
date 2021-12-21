from django.db.models import fields
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Comments, Group, GroupStudents, RatingCriteria, Ratings, SubGroup, TeamMember, Users


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        token['user_type_id_id'] = user.user_type_id_id
        return token


class UserSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    # email = serializers.EmailField(
    #     required=True
    # )
    # username = serializers.CharField()
    # password = serializers.CharField(min_length=8, write_only=True)
    class Meta:
        model = Users
        fields = ('id', 'email', 'password',
                  'first_name', 'last_name', 'user_type_id')
        # extra_kwargs = {'password': {'write_only': True}}


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'teacher_id', 'group_number',
                  'lesson_name', 'is_active', 'created_at')


class GroupStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStudents
        fields = ('id', 'group_id', 'student_id')


class SubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGroup
        fields = ('id', 'subgroup_name', 'group_id', 'deadline', 'is_active')


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'


# class TeamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model: Team
#         fields = ('subgroup_id', 'team_name')
class RatingCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingCriteria
        fields = ('id', 'rc_name', 'description', 'teacher_id', 'is_default')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = ('team_member_id', 'rc_name', 'rc_id',
                  'rating_value', 'comment_id')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('id', 'good_comm', 'bad_comm')
