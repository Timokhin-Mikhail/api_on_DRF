from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models import Avg
import zoneinfo
from dateutil import tz

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=200, blank=False, db_column='fullName')
    phone = models.CharField(max_length=11, blank=True, validators=[MinLengthValidator(11)])
    avatar = models.URLField(blank=True)
    # email = models.EmailField(default='no_email@no_email.com')


class Category(models.Model):
    title = models.CharField(max_length=200, blank=False)
    image = models.JSONField()
    maincategories = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='subcategories')

    def __str__(self):
        return str(self.id)


class Tag(models.Model):
    id = models.CharField(max_length=30, blank=False, unique=True, primary_key=True)
    name = models.CharField(max_length=30, blank=False)

    def __str__(self):
        return self.id


class Payment(models.Model):
    number = models.CharField(max_length=19, blank=False, null=False, validators=[MinLengthValidator(13),
                                                                                  RegexValidator(r'^\d+$')])
    name = models.CharField(max_length=200, blank=False, null=False)
    month = models.CharField(max_length=2, blank=False, null=False, validators=[MinLengthValidator(2),
                                                                                RegexValidator(r'^\d+$')])
    year = models.CharField(max_length=4, blank=False, null=False, validators=[MinLengthValidator(4),
                                                                               RegexValidator(r'^\d+$')])
    code = models.CharField(max_length=3, blank=False, null=False, validators=[MinLengthValidator(3),
                                                                               RegexValidator(r'^\d+$')])


class Image(models.Model):
    image = models.ImageField(upload_to="imgs")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.image.url


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=False, default=4, related_name='products')
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField()
    title = models.CharField(max_length=150, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True)
    fullDescription = models.TextField(blank=True)
    freeDelivery = models.BooleanField(default=True)
    limited = models.BooleanField(default=False)
    on_banner = models.BooleanField(default=False)
    images = GenericRelation(Image)
    tags = models.ManyToManyField(Tag, related_name='products')
    basket = models.ManyToManyField(User, through="Baskets", related_name='products')
    # href, rating создаем в anotate иногда

    def get_href(self):
        return f'catalog/{self.id}'

    def get_rating(self):
        rating = self.reviews.all().aggregate(Avg('rate'))['rate__avg']
        if not rating:
            rating = 0
        return round(rating, 2)

    def get_rev_count(self):
        return self.reviews.all().count()


class Baskets(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prod_count = models.PositiveIntegerField()
    price_mult_count = models.DecimalField(default=0, max_digits=12, decimal_places=2,
                                           validators=[MinValueValidator(0)])


class Review(models.Model):
    author = models.CharField(max_length=250, blank=False)
    email = models.EmailField(blank=False)
    text = models.TextField(blank=False)
    rate = models.SmallIntegerField(blank=False, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, blank=False, null=False, on_delete=models.CASCADE, related_name='reviews')


class Sales(models.Model):
    salePrice = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    dateFrom = models.DateField(auto_now_add=True)
    dateTo = models.DateField(auto_now_add=True)
    product = models.OneToOneField(Product, blank=False, null=False, on_delete=models.CASCADE, related_name='sale')
    # много полей вытаскиваем через product


class Specification(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=200)
    product = models.ManyToManyField(Product, related_name='specifications')


class Order(models.Model):
    orderId = models.CharField(max_length=30, primary_key=True)
    createdAt = models.DateTimeField()
    fullName = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=11, blank=True, validators=[MinLengthValidator(11)])
    deliveryType = models.CharField(max_length=30)
    paymentType = models.CharField(max_length=30)
    totalCost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')


class OrderProduct(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    category = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    date = models.CharField(max_length=200)
    title = models.CharField(max_length=150, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True)
    href = models.CharField(max_length=200)
    freeDelivery = models.BooleanField()
    images = models.JSONField()
    tags = models.JSONField()
    reviews = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')