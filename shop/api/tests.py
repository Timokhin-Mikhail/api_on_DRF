from django.contrib.contenttypes.models import ContentType

from api.models import Product



print(ContentType.objects.get(Product.objects.get(pk=1)).id)