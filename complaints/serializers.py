from rest_framework import serializers
from .models import RailwayComplaint, Department, Employee

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'department', 'email']

class RailwayComplaintSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    assigned_employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = RailwayComplaint
        fields = ['id', 'image', 'description', 'category', 'department', 'assigned_employee', 'created_at']
        read_only_fields = ['description', 'category', 'department', 'assigned_employee']
