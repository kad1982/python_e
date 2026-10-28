from category.models import Category


def categories(request):
    """Передает список всех категорий во все шаблоны, подключен в settings - templates"""
    return {
        'global_categories': Category.objects.all()
    }
