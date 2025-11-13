import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from projects.models import Project
from tasks.models import Task
from users.decorators import class_require_authentication
from rest_framework import serializers
from datetime import datetime, timezone

from users.models import Permission, User


class CreateTaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=5000, required=False)
    due_date = serializers.DateTimeField(required=True)
    status = serializers.ChoiceField(
        choices=Task.get_statuses(), required=True)
    priority = serializers.ChoiceField(
        choices=Task.get_priorities(), required=True)
    assigned_to_user_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)

    def validate_due_date(self, value):
        now = datetime.now(timezone.utc)
        if value <= now:
            raise serializers.ValidationError(
                "Due date must be in the future.")
        return value

    def validate_assigned_to_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Assigned user does not exist.")
        return value

    def validate_project_id(self, value):
        from projects.models import Project
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project does not exist.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'project', 'assigned_to_user', 'title',
                  'description', 'status', 'priority', 'due_date']


class TaskView(View):

    @class_require_authentication(Permission.CREATE_TASK)
    def post(self, request):
        data = json.loads(request.body)
        serializer = CreateTaskSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

        task = Task.objects.create(
            title=serializer.validated_data.get('title'),
            description=serializer.validated_data.get('description', ''),
            due_date=serializer.validated_data.get('due_date'),
            assign_to_user_id=serializer.validated_data.get(
                'assigned_to_user_id'),
            project_id=serializer.validated_data.get('project_id'),
            status=serializer.validated_data.get('status'),
            priority=serializer.validated_data.get('priority')
        )

        if not isinstance(task, Task):
            return JsonResponse({"code": 500, "data": [], "messages": "Task creating failure."}, status=200)

        return self.get(request, "Task created successfully.")

    @class_require_authentication(Permission.UPDATE_TASK)
    def put(self, request, task_id):

        task = Task.objects.filter(id=task_id).first()
        if not isinstance(task, Task):
            return JsonResponse({"code": 404, "data": [], "messages": "Task not found."}, status=200)

        data = json.loads(request.body)
        serializer = CreateTaskSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"code": 401, "data": [], "messages": serializer.errors}, status=200)

        for attr, value in serializer.validated_data.items():
            setattr(task, attr, value)

        task.save()

        return self.get(request, "Task updated successfully.")

    @class_require_authentication(Permission.DELETE_TASK)
    def delete(self, request, task_id):

        task = Task.objects.filter(id=task_id).first()
        if not isinstance(task, Task):
            return JsonResponse({"code": 404, "data": [], "messages": "Task not found."}, status=200)

        task.delete()

        return self.get(request, "Task deleted successfully.")

    @class_require_authentication(Permission.VIEW_TASKS)
    def get(self, request, message=""):
        object_list = Task.objects.all()
        per_page = request.GET.get('per_page', 5)
        paginator = Paginator(object_list, per_page)

        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        projects_data = [TaskSerializer(
            p).data for p in page_obj.object_list]

        return JsonResponse({"code": 200, "data": {
            "current_page": page_number,
            "data": projects_data,
            "per_page": per_page,
            "total": object_list.count()
        }, "messages": message}, status=200)
