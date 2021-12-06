from django.contrib.auth.models import User
from django.db.models.fields import EmailField
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .models import UserType, Users, GroupStudents

class ObtainTokenPair(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = Users.objects._create_user(**serializer.data)
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        elif Users.objects.filter(email = request.data['email']).exists():
            user = Users.objects.get(email = request.data['email'])
            serializer = UserSerializer(user)
            data = serializer.data
            if data['password']=="":
                user = Users.objects._create_user(**request.data)
                return Response(user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelloWorldView(APIView):
    """
        Test class
    """
    def get(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)


class CreateGroup(APIView):
    """
        Групп үүсгэхэд шаардлагатай утгуудыг авч үүсгэнэ. 
        Группд хамаарах оюутан бүртгэлтэй эсэхийг шалгаж бүртгэлгүй тохиолдолд зөвхөн email багана нь утгатай
        шинэ бичлэг Users дотор үүсгэн id-г нь GroupStudents-рүү ref болгон өгнө.
    """
    
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()


    def post(self, request, format='json'):
        data = request.data
        stud_list = data['student_list']
        data.pop('student_list')

        
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            group = serializer.save()

            for i in stud_list:
                user = Users.objects.get_or_create(email=i, defaults={'email':i, 'user_type_id':UserType.objects.get(user_type_name='Оюутан')})
                if user:
                    user = Users.objects.get(email=i)
                    GroupStudents.objects.create(student_id = user, group_id = group)
                else:
                    Users.object._create_user(email=i)

            if group:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)

class SubGroup(APIView):
    ### permission classuud daraa n ustgah ###
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    def post(self, request, format='json'):
        data = request.data

        serializer = SubGroupSerializer(data = data)
        if serializer.is_valid():
            subgroup = serializer.save()

            if subgroup:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
