from django.db import models


class Role(models.Model):

    ADMIN_ROLE = 'admin'
    MANAGER_ROLE = 'manager'
    MEMBER_ROLE = 'member'

    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(
        'Permission', through='RolePermission', related_name='role_permissions', blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_roles():
        return [Role.ADMIN_ROLE, Role.MANAGER_ROLE, Role.MEMBER_ROLE]

    class Meta:
        db_table = 'roles'


class Permission(models.Model):

    VIEW_OVERVIEW = 'view-overview'
    VIEW_PROJECTS = 'view-projects'
    CREATE_PROJECT = 'create-project'
    UPDATE_PROJECT = 'update-project'
    DELETE_PROJECT = 'delete-project'
    VIEW_TASKS = 'view-tasks'
    CREATE_TASK = 'create-task'
    UPDATE_TASK = 'update-task'
    DELETE_TASK = 'delete-task'
    UPDATE_TASK_STATUS = 'update-task-status'
    VIEW_USERS = 'view-users'
    CREATE_USER = 'create-user'
    UPDATE_USER = 'update-user'
    VIEW_CHAT = 'view-chat'
    VIEW_SETTINGS = 'view-settings'
    UPDATE_SETTINGS = 'update-settings'

    ALL_PERMISSIONS = [
        VIEW_OVERVIEW,
        VIEW_PROJECTS,
        CREATE_PROJECT,
        UPDATE_PROJECT,
        DELETE_PROJECT,
        VIEW_TASKS,
        CREATE_TASK,
        UPDATE_TASK,
        DELETE_TASK,
        UPDATE_TASK_STATUS,
        VIEW_USERS,
        CREATE_USER,
        UPDATE_USER,
        VIEW_CHAT,
        VIEW_SETTINGS,
        UPDATE_SETTINGS,
    ]

    ROLE_DEFAULT_PERMISSIONS = {
        Role.ADMIN_ROLE: [
            VIEW_OVERVIEW,
            VIEW_PROJECTS,
            CREATE_PROJECT,
            UPDATE_PROJECT,
            DELETE_PROJECT,
            VIEW_TASKS,
            CREATE_TASK,
            UPDATE_TASK,
            DELETE_TASK,
            UPDATE_TASK_STATUS,
            VIEW_USERS,
            CREATE_USER,
            UPDATE_USER,
            VIEW_CHAT,
            VIEW_SETTINGS,
            UPDATE_SETTINGS,
        ],
        Role.MANAGER_ROLE: [
            VIEW_OVERVIEW,
            VIEW_PROJECTS,
            CREATE_PROJECT,
            UPDATE_PROJECT,
            DELETE_PROJECT,
            VIEW_TASKS,
            CREATE_TASK,
            UPDATE_TASK,
            DELETE_TASK,
            UPDATE_TASK_STATUS,
            VIEW_CHAT,
            VIEW_SETTINGS,
            UPDATE_SETTINGS,
        ],
        Role.MEMBER_ROLE: [
            VIEW_OVERVIEW,
            VIEW_PROJECTS,
            VIEW_TASKS,
            UPDATE_TASK_STATUS,
            VIEW_CHAT,
            VIEW_SETTINGS,
            UPDATE_SETTINGS,
        ]
    }

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'permissions'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'role_permissions'


class User(models.Model):
    full_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    permissions = models.ManyToManyField(
        Permission, through='UserPermission', related_name='user_permissions', blank=True)

    def __str__(self):
        return self.full_name

    def has_permission(self, permission_name):
        return self.permissions.filter(name=permission_name).exists()

    def get_password(self):
        return self.password

    class Meta:
        db_table = 'users'


class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_permissions'
