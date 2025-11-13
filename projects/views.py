import json
from django.http import JsonResponse
from django.views import View
from rest_framework import serializers
from projects.models import Project
from users.decorators import class_require_authentication
from django.core.paginator import Paginator
from datetime import datetime, timezone

from users.models import Permission


class CreateProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=5000, required=False)
    due_date = serializers.DateTimeField(required=True)

    def validate_due_date(self, value):
        now = datetime.now(timezone.utc)
        if value <= now:
            raise serializers.ValidationError(
                "Due date must be in the future.")
        return value


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'due_date']


class ProjectView(View):

    @class_require_authentication(Permission.CREATE_PROJECT)
    def post(self, request):
        data = json.loads(request.body)
        serializer = CreateProjectSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

        project = Project.objects.create(
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description', ''),
            due_date=serializer.validated_data.get('due_date'),
            creator=request.user
        )

        if not isinstance(project, Project):
            return JsonResponse({"code": 500, "data": [], "messages": "Project creating failure."}, status=200)

        return self.get(request, "Project created successfully.")

    @class_require_authentication(Permission.UPDATE_PROJECT)
    def put(self, request, project_id):

        project = Project.objects.filter(id=project_id).first()
        if not isinstance(project, Project):
            return JsonResponse({"code": 404, "data": [], "messages": "Project not found."}, status=200)

        data = json.loads(request.body)
        serializer = CreateProjectSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

        for attr, value in serializer.validated_data.items():
            setattr(project, attr, value)

        project.save()

        return self.get(request, "Project updated successfully.")

    @class_require_authentication(Permission.DELETE_PROJECT)
    def delete(self, request, project_id):

        project = Project.objects.filter(id=project_id).first()
        if not isinstance(project, Project):
            return JsonResponse({"code": 404, "data": [], "messages": "Project not found."}, status=200)

        project.delete()

        return self.get(request, "Project deleted successfully.")

    @class_require_authentication(Permission.VIEW_PROJECTS)
    def get(self, request, message=""):
        object_list = Project.objects.all()
        per_page = request.GET.get('per_page', 5)
        paginator = Paginator(object_list, per_page)

        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        projects_data = [ProjectSerializer(
            p).data for p in page_obj.object_list]

        return JsonResponse({"code": 500, "data": {
            "current_page": page_number,
            "data": projects_data,
            "per_page": per_page,
            "total": object_list.count()
        }, "messages": message}, status=200)
