from rest_framework import serializers
from api.models import Profile, Category, Tag, Payment, Product, Image, Review, Specification, Baskets, Sales, \
    OrderProduct, Order
from django.db.models import Value,  CharField
from django.db.models.functions import Concat
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def update(self, instance, validated_data):
        instance.user.email = validated_data.get('user', {}).get('email', False) or instance.user.email
        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.user.save()
        instance.save()
        return instance


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[validate_password])

    def update(self, instance, validated_data):
        instance.user.set_password(validated_data.get('password'))
        instance.user.save()
        return instance


class AvatarSerializer(serializers.Serializer):
    url = serializers.URLField()

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('url', instance.avatar)
        instance.save()
        return instance


class ForSubCategorySerializer(serializers.ModelSerializer):
    href = serializers.CharField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'href')


class SubCategoriesSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        value = Category.objects.filter(pk=value.pk).\
            annotate(href=Concat(Value('/catalog/'), 'id', output_field=CharField())).get()
        serializer = ForSubCategorySerializer(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategoriesSerializer(many=True)
    href = serializers.CharField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'href', 'subcategories')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class Paymenterializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        exclude = ['id']


class ImageObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Product):
            serializer = ProductSerializer(value)

        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']


class ProductsSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True)
    href = serializers.CharField()
    id = serializers.CharField()
    category = serializers.StringRelatedField()
    rating = serializers.FloatField()
    reviews = serializers.IntegerField(source='reviews.count', read_only=True)
    date = serializers.DateTimeField(format="%a %b %d %m %Y %H:%M:%S GMT%z")

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'href', 'freeDelivery', 'images',
                  'tags', 'reviews', 'rating']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']

    def create(self, validated_data):
        validated_data['product_id'] = self.context['view'].kwargs['pk']
        return Review.objects.create(**validated_data)


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True)
    href = serializers.CharField()
    id = serializers.CharField()
    category = serializers.StringRelatedField()
    rating = serializers.FloatField()
    reviews = ReviewSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription', 'href',
                  'freeDelivery', 'images', 'tags', 'reviews', 'specifications', 'rating']


class BasketProductsSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='product.id')
    category = serializers.StringRelatedField(source='product.category')
    price = serializers.DecimalField(source='price_mult_count', max_digits=12, decimal_places=2)
    count = serializers.IntegerField(source='prod_count')
    date = serializers.DateTimeField(source='product.date', format="%a %b %d %m %Y %H:%M:%S")
    title = serializers.CharField(source='product.title')
    description = serializers.CharField(source='product.description')
    freeDelivery = serializers.BooleanField(source='product.freeDelivery')
    images = serializers.StringRelatedField(source='product.images', many=True)
    tags = serializers.StringRelatedField(source='product.tags', many=True)
    href = serializers.CharField(source='product.get_href')
    reviews = serializers.IntegerField(source='product.get_rev_count')
    rating = serializers.DecimalField(source='product.get_rating', max_digits=3, decimal_places=2)

    class Meta:
        model = Baskets
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'href', 'freeDelivery', 'images',
                  'tags', 'reviews', 'rating']


class BasketChangesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField(validators=[MinValueValidator(1)])


class JustBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baskets
        exclude = ['id']


class SalesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product.id')
    price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2)
    title = serializers.CharField(source='product.title')
    href = serializers.CharField(source='product.get_href')
    images = serializers.StringRelatedField(source='product.images', many=True)

    class Meta:
        model = Sales
        fields = ['id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'href', 'images']


class OrderProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        exclude = ['order']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    createdAt = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    # user = serializers.IntegerField(source='user.id', write_only=True)

    class Meta:
        model = Order
        fields = ["orderId", "createdAt",  "fullName", "email", "phone", "deliveryType", "paymentType", "totalCost",
                   "status",  "city", "address", "products"]

    def create(self, validated_data):
        user = self.context['request'].user
        products = validated_data.pop('products')
        order = Order.objects.create(user=user, **validated_data)
        for product in products:
            OrderProduct.objects.create(order=order,  **product)

        return order
