"""Test models for djadmin-filters tests."""

from django.db import models


class Category(models.Model):
    """Test category model for filtering tests."""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Test product model for filtering tests."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return self.name
