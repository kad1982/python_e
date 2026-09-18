from django.shortcuts import render
from django.template.defaultfilters import title

from .models import Product


# Create your views here.
def product_list(request):
    category = request.GET.get('category', 'all')
    if category == 'all':
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category__name=category)
    if not products.exists():
        pass

    context = {'products': products, 'category': category}
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    context = {'product': product}
    return render(request, 'products/product_detail.html', context)
