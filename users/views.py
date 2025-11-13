from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import jwt
from rest_framework import serializers
import json
from django.contrib.auth.hashers import make_password, check_password

from core import settings
from users.decorators import require_authentication
from users.models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role']


class SignUpSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, min_length=8)


@require_http_methods(['POST'])
def signup(request):

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST.dict()

    serializer = SignUpSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

    memberRole = Role.objects.get(name=Role.MEMBER_ROLE)

    if not isinstance(memberRole, Role):
        return JsonResponse({"code": 500, "data": [], "messages": "Sign up failure."}, status=200)

    user = User.objects.create(
        full_name=serializer.validated_data['full_name'],
        email=serializer.validated_data['email'],
        password=make_password(serializer.validated_data['password']),
        role=memberRole
    )

    if not isinstance(user, User):
        return JsonResponse({"code": 500, "data": [], "messages": "Sign up failure."}, status=200)

    user.permissions.set(memberRole.permissions.all())

    access_token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now() + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm="HS256"
    )

    user_data = UserSerializer(user).data
    return JsonResponse({"code": 200, "data": {"token": access_token, "user": user_data}, "messages": "Sign up successful."}, status=200)


@require_http_methods(['POST'])
def signin(request):

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST.dict()

    serializer = SignInSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

    user = User.objects.filter(
        email=serializer.validated_data['email']).first()
    if not isinstance(user, User) or not check_password(serializer.validated_data['password'], user.get_password()):
        return JsonResponse({"code": 500, "data": [], "messages": "Invalid creadentials."}, status=200)

    access_token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now() + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm="HS256"
    )

    user_data = UserSerializer(user).data
    return JsonResponse({"code": 200, "data": {"token": access_token, "user": user_data}, "messages": "Sign in successful."}, status=200)


@require_authentication()
@require_http_methods(['GET'])
def authenticate(request):
    user_data = UserSerializer(request.user).data
    return JsonResponse({"code": 200, "data": user_data, "messages": "Authenticated successfully."}, status=200)
