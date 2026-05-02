from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username


class Budget(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student.user.username} - {self.category}"


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    )

    INCOME_CATEGORIES = [
        ('Salary', 'Salary'),
        ('Allowance', 'Allowance'),
        ('Business', 'Business'),
        ('Freelance', 'Freelance'),
        ('Others', 'Others'),
    ]

    EXPENSE_CATEGORIES = [
        ('Food', 'Food'),
        ('Transportation', 'Transportation'),
        ('Bills', 'Bills'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Health', 'Health'),
        ('Education', 'Education'),
        ('Groceries', 'Groceries'),
        ('Dining Out', 'Dining Out'),
        ('Others', 'Others'),
    ]

    ALL_CATEGORIES = INCOME_CATEGORIES + EXPENSE_CATEGORIES

    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.category} - {self.amount}"