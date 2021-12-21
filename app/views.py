from django.contrib.auth.models import User
from django.db.models.fields import EmailField
from django.core import serializers as core_serializers
from django.utils.functional import Promise
from rest_framework import permissions, status
from rest_framework import response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
import json


class ObtainTokenPair(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserCreate(APIView):
    """
        Хэрэглэгч бүртгэх класс. Өмнө нь бүртгэлгүй байсан бол шууд бүртгэнэ.
        Хэрэв багш Group-д нэмэхдээ бүртэгсэн бол тухайн мөр бичлэгийг олон update хийнэ.
    """
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = Users.objects._create_user(**serializer.data)
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)

        elif Users.objects.filter(email=request.data['email']).exists():
            user = Users.objects.get(email=request.data['email'])
            us_serializer = UserSerializer(user)
            password = us_serializer.data['password']
            if password == "":
                user = Users.objects.create_preuser(**request.data)
                json = {'msg': 'succesfully created pre user'}
                return Response(json)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Groups(APIView):
    """
        Групп үүсгэхэд шаардлагатай утгуудыг авч үүсгэнэ.
        Группд хамаарах оюутан бүртгэлтэй эсэхийг шалгаж бүртгэлгүй тохиолдолд зөвхөн email багана нь утгатай
        шинэ бичлэг Users дотор үүсгэн id-г нь GroupStudents-рүү ref болгон өгнө.
    """

    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['teacher_id']
        print(data)
        try:
            groups = Group.objects.filter(teacher_id=data)
        except Group.DoesNotExist:
            groups = None
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format='json'):
        data = request.data
        print(data)
        students = data['student_list'].strip()
        stud_list = list(students.split("\n"))
        stud_list = [i.strip() for i in stud_list]
        data.pop('student_list')
        print(stud_list)
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            group = serializer.save()

            for i in stud_list:
                user = Users.objects.get_or_create(email=i.strip(), defaults={
                                                   'email': i, 'user_type_id': UserType.objects.get(user_type_name='Оюутан')})
                if user:
                    user = Users.objects.get(email=i)
                    GroupStudents.objects.create(
                        student_id=user, group_id=group)
                else:
                    Users.object._create_user(email=i)

            if group:
                json = serializer.data
                json['id'] = group.id
                return Response(json, status=status.HTTP_201_CREATED)


class GroupStudentGetStudent(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['student_id']

        try:
            subgroups = GroupStudents.objects.filter(student_id=data)
            serializer = GroupStudentSerializer(subgroups, many=True)

            id_list = [i['group_id'] for i in serializer.data]
            students = Group.objects.filter(id__in=id_list)
            serializer = GroupSerializer(students, many=True)
        except GroupStudents.DoesNotExist:
            subgroups = None
            serializer = GroupStudentSerializer(subgroups, many=True)
        return Response(serializer.data)


class GroupStudent(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['group_id']

        try:
            subgroups = GroupStudents.objects.filter(group_id=data)
            serializer = GroupStudentSerializer(subgroups, many=True)

            id_list = [i['student_id'] for i in serializer.data]
            students = Users.objects.filter(id__in=id_list)
            serializer = UserSerializer(students, many=True)
        except GroupStudents.DoesNotExist:
            subgroups = None
            serializer = GroupStudentSerializer(subgroups, many=True)
        return Response(serializer.data)


class SubGroups(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['group_id']

        try:
            subgroups = SubGroup.objects.filter(group_id=data)
        except SubGroup.DoesNotExist:
            subgroups = None
        serializer = SubGroupSerializer(subgroups, many=True)
        return Response(serializer.data)

    def post(self, request, format='json'):
        data = request.data
        print(data)
        serializer = SubGroupSerializer(data=data)
        print(serializer)
        if serializer.is_valid():
            subgroup = serializer.save()

            if subgroup:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMembers(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['subgroup_id']
        try:
            team_members = TeamMember.objects.filter(subgroup_id=data)
            serializer = TeamMemberSerializer(team_members, many=True)
            data = serializer.data
            team_members = json.loads(json.dumps(data))
            for i in team_members:
                student = GroupStudents.objects.filter(
                    id=i['group_student_id'])
                student_serializer = GroupStudentSerializer(student, many=True)
                student_info = dict(student_serializer.data[0])
                more_info_student = Users.objects.filter(
                    id=student_info['student_id'])
                s_more_info_serializer = UserSerializer(
                    more_info_student, many=True)

                student_more_info = dict(s_more_info_serializer.data[0])
                i['student_info'] = student_more_info
            final_data = [{'id': i['id'], 'team_name':i['team_name'], 'email':i['student_info']['email'],
                           'first_name':i['student_info']['first_name'], 'last_name':i['student_info']['last_name'], }for i in team_members]
            d = {}
            for item in final_data:
                d.setdefault(item['team_name'], []).append(item)

            list(d.values())
            return Response(d)
        except GroupStudents.DoesNotExist:
            teammembers = None
            serializer = TeamMemberSerializer(teammembers, many=True)
            return Response(serializer.data)

    def post(self, request, format='json'):
        data = request.data
        subgroup_id = data['subgroup_id']
        group_id = data['group_id']
        raw_list = data['team_list']
        updated_list = []
        for i in raw_list:
            for j in i['selected']:
                updated_list.append({'team_name': str(i['id'])+'-р баг',
                                    'subgroup_id': subgroup_id,
                                     'group_student_id': GroupStudents.objects.filter(student_id=j['value'], group_id=group_id).values_list('pk', flat=True)[0]})
        for team in updated_list:
            serializer = TeamMemberSerializer(data=team)
            json = ''
            if serializer.is_valid():
                team_member = serializer.save()

                if team_member:
                    json = serializer.data
        return Response(json, status=status.HTTP_201_CREATED)


class MyTeam(APIView):

    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        data = request.query_params['subgroup_id']
        student_id = request.query_params['user_id']
        group_id = request.query_params['group_id']
        team_list = []
        try:
            student = GroupStudents.objects.filter(student_id=student_id)
            student_serializer = GroupStudentSerializer(student, many=True)
            team = TeamMember.objects.get(
                group_student_id=GroupStudents.objects.get(student_id=student_id, group_id=group_id))
            serializer = TeamMemberSerializer(team)
            data = serializer.data
            student_info = json.loads(json.dumps(data))
            team_members = TeamMember.objects.filter(
                subgroup_id=student_info['subgroup_id'], team_name=student_info['team_name']).values()
            for i in team_members:
                std_id = GroupStudents.objects.filter(id=i['group_student_id_id']).values()[
                    0]['student_id_id']
                student_info = Users.objects.get(id=std_id)
                serializer = UserSerializer(student_info)
                student_data = serializer.data
                if student_data['id'] != int(student_id):
                    team_list.append({'first_name': student_data['first_name'],
                                      'last_name': student_data['last_name'],
                                      'student_id': student_data['id'],
                                      'group_student_id': i['group_student_id_id'],
                                      'team_member_id': i['id'],
                                      'email': student_data['email']})
            real_final_shit = {
                'team_name': team_members[0]['team_name'], 'team_members': team_list}
            return Response(real_final_shit)
        except GroupStudents.DoesNotExist:
            teammembers = None
            serializer = TeamMemberSerializer(teammembers, many=True)
            return Response(serializer.data)


class Teams(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    # def get(self, request, format='json'):
    #     data = request.query_params['group_id']

    #     try:
    #         subgroups = SubGroup.objects.filter(group_id=data)
    #     except SubGroup.DoesNotExist:
    #         subgroups = None
    #     serializer = SubGroupSerializer(subgroups, many=True)
    #     return Response(serializer.data)

    # def post(self, request, format='json'):
    #     data = request.data
    #     print(data)
    #     serializer = TeamSerializer(data=data)
    #     if serializer.is_valid():
    #         team = serializer.save()

    #         if team:
    #             json = serializer.data
    #             return Response(json, status=status.HTTP_201_CREATED)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingCriterias(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        try:
            rc = RatingCriteria.objects.all()
        except Group.DoesNotExist:
            rc = None
        serializer = RatingCriteriaSerializer(rc, many=True)
        return Response(serializer.data)


class GroupRatings(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, format='json'):
        subgroup_id = request.query_params['subgroup_id']
        group_id = request.query_params['group_id']
        team_list = []

        team_member = TeamMember.objects.filter(
            group_student_id__group_id=group_id, subgroup_id=subgroup_id).values()
        for i in team_member:
            rating = Ratings.objects.filter(
                team_member_id=i['id']).values('rating_value')
            rating_list = [d['rating_value'] for d in rating]
            if rating_list:
                avg_value = sum(rating_list) / len(rating_list)
                avg_decimal = float("{:.2f}".format(avg_value))
                i['avg_value'] = avg_decimal
            else:
                i['avg_value'] = 0
            group_students = GroupStudents.objects.filter(
                id=i['group_student_id_id']).values()
            student_id = group_students[0]['student_id_id']
            student_info = Users.objects.filter(id=student_id).values()
            i['first_name'] = student_info[0]['first_name']
            i['email'] = student_info[0]['email']
            print(student_info)

        # ratings = Ratings.objects.filter(
        #     team_member_id__in=group_students).values()

        # rating_ser = RatingSerializer(data=ratings)
        # print(rating_ser)
        # if rating_ser.is_valid():
        return Response(team_member)


class Rating(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        data = request.data['post_list']
        good_comm = request.data['good_comm']
        bad_comm = request.data['bad_comm']

        comment = Comments.objects.create(
            bad_comm=bad_comm, good_comm=good_comm)
        for i in data:
            i['comment_id'] = comment.id
            print(i)
            serializer = RatingSerializer(data=i)
            if serializer.is_valid():
                rating = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'success'})
