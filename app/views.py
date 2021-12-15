from django.contrib.auth.models import User
from django.db.models.fields import EmailField
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .models import *


class ObtainTokenPair(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


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
                json = UserSerializer(data=user)
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
        stud_list = list(students.split(" "))
        data.pop('student_list')

        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            group = serializer.save()

            for i in stud_list:
                user = Users.objects.get_or_create(email=i, defaults={
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


class TeamMember(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        data = request.data

        serializer = TeamMemberSerializer(data=data)
        if serializer.is_valid():
            team_member = serializer.save()

            if team_member:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)


class Rating(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        data = request.data

        serializer = TeamMemberSerializer(data=data)
        if serializer.is_valid():
            rating = serializer.save()

            if rating:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
