from category.models import Category


def categories(request):
    """Передает список всех категорий во все шаблоны"""
    return {
        'global_categories': Category.objects.all()
    }
