from django.db import models

class Student(models.Model):
    COURSE_CHOICES = (
        ('WEB', 'Web Development'),
        ('AI', 'AI & Automation'),
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    join_date = models.DateField()

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    in_time = models.TimeField(blank=True, null=True)
    out_time = models.TimeField(blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


class Expense(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"
