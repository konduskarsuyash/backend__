from django.contrib import admin
from .models import Department, Employee, RailwayComplaint

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'department', 'email']
    list_filter = ['department']

@admin.register(RailwayComplaint)
class RailwayComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'category', 'department', 'assigned_employee', 'created_at']
    list_filter = ['category', 'department', 'assigned_employee']
