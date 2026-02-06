from rest_framework import serializers
from .models import Buying, QuickSale, Revenue, UserAccount, Cashier, Role, Expense,Exchange, SubCategory, Electronics, Sales, Category, SalesSummary
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['role'] = user.role
        
        return token



# serializers.py
class QuickSaleSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    item_available_quantity = serializers.IntegerField(source='item.quantity', read_only=True)

    class Meta:
        model = QuickSale
        fields = '__all__'
        read_only_fields = ('is_completed', 'created_at', 'completed_at', 'buying_price')

    def validate(self, data):
        # Only validate required fields when completing the sale, not when creating
        if self.instance and self.instance.is_completed:
            if not data.get('selling_price'):
                raise serializers.ValidationError("Selling price is required to complete the sale.")
            if not data.get('payment_method'):
                raise serializers.ValidationError("Payment method is required to complete the sale.")
            if not data.get('status'):
                raise serializers.ValidationError("Status is required to complete the sale.")
        return data
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'name', 'is_active', 'role']
        # Do not include 'password' in this serializer to avoid security issues

class CashierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashier
        fields = ['email', 'name', 'phone_number']  # Exclude password field

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
        fields = ('id', 'email', 'name', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', '')  # Ensure role is included
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ('id', 'email', 'name', 'role')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class ElectronicsSerializer(serializers.ModelSerializer):
    delete_image = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Electronics
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('delete_image', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        delete_image = validated_data.pop('delete_image', False)
        if delete_image:
            # Delete physical file is handled by pre_save signal if we set image to None?
            # Actually pre_save handles *change*, but we need to ensure setting it to None triggers it.
            # Or manually delete here. Let's rely on the signal logic (change from Something -> None).
            instance.image = None
        
        return super().update(instance, validated_data)

class BuyingSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Buying
        fields = [
            'id', 'main_category', 'sub_category', 'name', 'size', 
            'quantity', 'added_by', 'buying_price', 'date_added',
            'supplier', 'purchase_order', 'notes',
            'main_category_name', 'sub_category_name', 'total_cost'
        ]
        read_only_fields = ['id', 'date_added']

    def get_total_cost(self, obj):
        return float(obj.buying_price) * obj.quantity
    
    
class SalesSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    item_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Sales
        fields = '__all__'

    def get_item_image(self, obj):
        # Try to find the item by name. Warning: This assumes names are unique enough.
        # Ideally, Sales should have a ForeignKey to Electronics.
        item = Electronics.objects.filter(name=obj.item_name).first()
        if item and item.image:
            return item.image.url
        return None
        
class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exchange
        fields = '__all__'

class SalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSummary
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = '__all__'
