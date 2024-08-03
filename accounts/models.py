from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def create_default_roles():
        Role.objects.get_or_create(name='Admin')
        Role.objects.get_or_create(name='Cashier')

    @classmethod
    def get_role_by_name(cls, name):
        return cls.objects.filter(name=name).first()

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_superuser(self, email, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)
    #
    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')
    #
    #     return self.create_user(email, password, **extra_fields)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=255)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email

    def remove_permissions(self):
        """
        Remove all user permissions.
        """
        self.user_permissions.clear()  # Clear all permissions associated with the user

    def remove_groups(self):
        """
        Remove the user from all groups.
        """
        self.groups.clear()  # Clear all groups associated with the user
class Cashier(UserAccount):
    phone_number = models.CharField(max_length=15, unique=True)  # Add phone number field

    def __str__(self):
        return f"Cashier: {self.name}"

# /*  class Admin(UserAcccount): if we want additional attributes for Admin we can add here and it inhereited from userAccount*
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    main_category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Electronics(models.Model):
    category = models.ForeignKey(Category, related_name='electronics', on_delete=models.CASCADE)
    sub_category = models.ForeignKey( SubCategory ,related_name='electronics', on_delete=models.CASCADE )
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()  # Represents stock
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    # selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # Added selling price for clarity
    # Add any other relevant fields

    def __str__(self):
        return self.name

class Sales(models.Model):
    item_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='sales', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='sales', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateField()  # Date of the expense
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller_name = models.CharField(max_length=255)

    def __str__(self):
        return self.item_name
class SalesSummary(models.Model):
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Summary for {self.date}"

class Expense(models.Model):
    name = models.CharField(max_length=255)  # Expense name
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount
    date = models.DateField()  # Date of the expense
    description = models.TextField(blank=True, null=True)  # Optional description
    is_verified = models.BooleanField(default=False)  # Verification status

    def __str__(self):
        return self.name
