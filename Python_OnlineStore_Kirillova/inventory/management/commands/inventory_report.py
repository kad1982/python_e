from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg, Q
from ...models import Inventory
from products.models import Category  # Добавляем импорт Category


class Command(BaseCommand):
    help = 'Отчет по остаткам товаров'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Отчет по конкретной категории'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Экспортировать отчет в файл'
        )

    def handle(self, *args, **options):
        category_filter = options.get('category')
        export_file = options.get('export')

        # Используем select_related для оптимизации запросов
        queryset = Inventory.objects.select_related('product', 'product__category').all()

        if category_filter:
            # Ищем по названию категории через связанную модель
            # Правильно: product__category__name__icontains
            queryset = queryset.filter(product__category__name__icontains=category_filter)
            self.stdout.write(f'📊 Отчет по категории: {category_filter}')

        # Статистика
        total_items = queryset.count()
        total_quantity = queryset.aggregate(total=Sum('quantity'))['total'] or 0
        total_reserved = queryset.aggregate(total=Sum('reserved_quantity'))['total'] or 0
        total_available = total_quantity - total_reserved

        avg_price = queryset.filter(product__price__isnull=False).aggregate(
            avg=Avg('product__price')
        )['avg'] or 0

        # Товары с нулевым остатком
        zero_stock = queryset.filter(quantity=0)

        # Товары с большим резервом
        high_reserved = queryset.filter(reserved_quantity__gt=0)

        # Формируем отчет
        report = []
        report.append('=' * 70)
        report.append('📊 ОТЧЕТ ПО ОСТАТКАМ ТОВАРОВ')
        report.append('=' * 70)
        report.append(f'📦 Всего товаров: {total_items}')
        report.append(f'📦 Общее количество: {total_quantity} шт.')
        report.append(f'📦 Зарезервировано: {total_reserved} шт.')
        report.append(f'📦 Доступно: {total_available} шт.')
        report.append(f'💰 Средняя цена: {avg_price:.2f} руб.')
        report.append('=' * 70)

        if zero_stock.exists():
            report.append('⚠️ ТОВАРЫ С НУЛЕВЫМ ОСТАТКОМ:')
            for item in zero_stock[:10]:
                category_name = item.product.category.name if item.product.category else 'Без категории'
                report.append(f'  - {item.product.name} (Категория: {category_name})')
            if zero_stock.count() > 10:
                report.append(f'  ... и еще {zero_stock.count() - 10} товаров')
            report.append('')

        if high_reserved.exists():
            report.append('🔒 ТОВАРЫ С РЕЗЕРВОМ:')
            for item in high_reserved[:10]:
                report.append(f'  - {item.product.name}: {item.reserved_quantity} из {item.quantity} шт.')
            if high_reserved.count() > 10:
                report.append(f'  ... и еще {high_reserved.count() - 10} товаров')
            report.append('')

        # Топ по остаткам
        report.append('🏆 ТОП-10 ПО КОЛИЧЕСТВУ:')
        for item in queryset.order_by('-quantity')[:10]:
            category_name = item.product.category.name if item.product.category else 'Без категории'
            report.append(f'  {item.quantity} шт. - {item.product.name} ({category_name})')

        report.append('=' * 70)

        # Выводим отчет
        output = '\n'.join(report)
        self.stdout.write(output)

        # Экспортируем если нужно
        if export_file:
            try:
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                self.stdout.write(self.style.SUCCESS(f'\n✅ Отчет сохранен в файл: {export_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при сохранении файла: {e}'))