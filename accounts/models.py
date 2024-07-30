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

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email

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
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    electronics = models.ForeignKey(Electronics, related_name='stocks', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=10)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_number = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.electronics.name} - {self.quantity} {self.units}"

class Sale(models.Model):
    stock = models.ForeignKey(Stock, related_name='sales', on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    sale_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total profit
        buying_price = self.stock.buying_price
        selling_price = self.stock.selling_price
        profit_per_item = selling_price - buying_price
        self.total_profit = profit_per_item * self.quantity_sold
        super(Sale, self).save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.quantity_sold} items from {self.stock.electronics.name}"
