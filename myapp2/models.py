from django.db import models
from django.contrib.auth.models import User

# Optional: Extra info for student if needed
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username


# Budget categories like Food, Transport, Entertainment, etc.
class Budget(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student.user.username} - {self.category}"


# Individual income or expense entries
class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    category = models.ForeignKey(Budget, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.transaction_type} - {self.amount}"
