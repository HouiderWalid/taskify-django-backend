from functools import wraps
from django.http import JsonResponse
import jwt
from core import settings
from users.models import User


def require_authentication(permission_required=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({"code": 500, "data": [], "messages": "Authentication credentials were not provided."}, status=200)

            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload['user_id'])

                if permission_required and not user.has_permission(permission_required):
                    return JsonResponse({"code": 500, "data": [], "messages": "You do not have permission to perform this action."}, status=200)

                request.user = user
            except jwt.ExpiredSignatureError:
                return JsonResponse({"code": 500, "data": [], "messages": "Token has expired."}, status=200)
            except jwt.InvalidTokenError:
                return JsonResponse({"code": 500, "data": [], "messages": "Invalid token."}, status=200)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def class_require_authentication(permission_required=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({"code": 500, "data": [], "messages": "Authentication credentials were not provided."}, status=200)

            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload['user_id'])

                if permission_required and not user.has_permission(permission_required):
                    return JsonResponse({"code": 500, "data": [], "messages": "You do not have permission to perform this action."}, status=200)

                request.user = user
            except jwt.ExpiredSignatureError:
                return JsonResponse({"code": 500, "data": [], "messages": "Token has expired."}, status=200)
            except jwt.InvalidTokenError:
                return JsonResponse({"code": 500, "data": [], "messages": "Invalid token."}, status=200)

            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator
