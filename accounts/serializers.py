from rest_framework import serializers
from .models import UserAccount,Cashier, Role, Expense, SubCategory, Electronics, Sales,Category, SalesSummary

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'



class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'password', 'email', 'name', 'is_active', 'role']
class CashierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashier
        fields = ['email', 'name', 'password', 'phone_number']  # Include the new fields

    def create(self, validated_data):
        # Create a new cashier instance
        cashier = Cashier(
            email=validated_data['email'],
            name=validated_data['name'],
            phone_number=validated_data['phone_number']
        )
        cashier.set_password(validated_data['password'])  # Hash the password
        cashier.save()
        return cashier
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email', 'name', 'password', 'role']  # Include any other fields needed for creation
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class ElectronicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electronics
        fields = '__all__'

class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = ['id', 'item_name', 'category', 'sub_category', 'quantity','date', 'selling_price', 'seller_name']

class SalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSummary
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'