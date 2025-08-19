from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import datetime

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
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

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
        self.user_permissions.clear()

    def remove_groups(self):
        self.groups.clear()
    
class Cashier(UserAccount):
    phone_number = models.CharField(max_length=15, unique=True)

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
    main_category = models.ForeignKey(Category, related_name='electronics', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='electronics', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()  # Represents stock
    added_by = models.CharField(max_length=100 , null= True)

    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(default=datetime.date.today)
    

    # selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # Added selling price for clarity
    # Add any other relevant fields

    def __str__(self):
        return self.name
 
class Buying(models.Model):
    main_category = models.ForeignKey(Category, related_name='buying', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='buying', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()  # Represents stock
    added_by = models.CharField(max_length=100 , null= True)

    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(default=datetime.date.today)
    

    # selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # Added selling price for clarity
    # Add any other relevant fields

    def __str__(self):
        return self.name
 
class Sales(models.Model):
    item_name = models.CharField(max_length=255)
    main_category = models.ForeignKey(Category, related_name='sales', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='sales', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=50 ,null=True)

    date = models.DateField()  
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2 , null=True)
    seller_name = models.CharField(max_length=255)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    buyer_name = models.CharField(max_length=255 ,null=True, blank=True)
    status = models.CharField(null=True, max_length=50, choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
       
    ])  
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('debit', 'Debit'),
        ('telebirr', 'telebirr')
    ], default='cash')  

    def __str__(self):
        return self.item_name
class Exchange(models.Model):
    item_name = models.CharField(max_length=255)
    main_category = models.ForeignKey(Category, related_name='exchange_main_category', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='exchange_sub_category', on_delete=models.CASCADE)
    size = models.CharField(max_length=50 ,null=True)
    new_item_size = models.CharField(max_length=50 ,null=True)

    new_item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField(default=timezone.now)
    new_item_main_category = models.ForeignKey(Category, related_name='exchange_new_main_category', on_delete=models.CASCADE, null=True, blank=True)
    new_item_sub_category = models.ForeignKey(SubCategory, related_name='exchange_new_sub_category', null=True,on_delete=models.CASCADE)
    estimated_exchange_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    seller_name = models.CharField(max_length=255)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('debit', 'Debit'),
        ('telebirr', 'telebirr')
    ], default='cash')

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

class Revenue(models.Model):
    name = models.CharField(max_length=255)  # Expense name
    recievername = models.CharField(max_length=255)  # Expense name
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount
    date = models.DateField()  # Date of the expense
    description = models.TextField(blank=True, null=True)  # Optional description
    is_verified = models.BooleanField(default=False)  # Verification status
    reason = models.CharField(max_length=255 ,null=True, blank=True)
    def __str__(self):
        return self.name
