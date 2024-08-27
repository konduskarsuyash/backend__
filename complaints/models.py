from django.db import models
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r"^\+\d{12}$", message="Phone number must be in the format +919xxxxxxxxx and 12 digits after the '+' sign."
)

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(
        unique=True, max_length=13, null=False, blank=False, validators=[phone_regex]
    )
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"


    def __str__(self):
        return f"{self.name} ({self.department.name})"

class RailwayComplaint(models.Model):
    image = models.ImageField(upload_to='complaints/')
    description = models.TextField()
    category = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint {self.id} - {self.get_category_display()}"
