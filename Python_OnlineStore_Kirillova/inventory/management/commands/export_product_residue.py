import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.utils import timezone
from ...models import Inventory


class Command(BaseCommand):
    help = 'Экспорт остатков товаров в JSON файл'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Путь для сохранения JSON файла',
            default=f'fixtures/export_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['full', 'simple', 'detailed', 'django'],
            default='simple',
            help='Формат экспорта'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Экспортировать только указанную категорию'
        )
        parser.add_argument(
            '--min_quantity',
            type=int,
            help='Экспортировать только товары с остатком больше указанного'
        )
        parser.add_argument(
            '--max_quantity',
            type=int,
            help='Экспортировать только товары с остатком меньше указанного'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Экспортировать только указанный продукт'
        )
        parser.add_argument(
            '--warehouse',
            type=str,
            help='Экспортировать только с указанного склада'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        format_type = options['format']
        category_filter = options.get('category')
        min_quantity = options.get('min_quantity')
        max_quantity = options.get('max_quantity')
        name_filter = options.get('name')
        warehouse_filter = options.get('warehouse')

        # Формируем запрос
        queryset = Inventory.objects.select_related('product', 'product__category').all()

        # Применяем фильтры
        if category_filter:
            queryset = queryset.filter(product__category__name__icontains=category_filter)
            self.stdout.write(f'📂 Фильтр по категории: {category_filter}')

        if min_quantity is not None:
            queryset = queryset.filter(quantity__gte=min_quantity)
            self.stdout.write(f'📦 Фильтр по остатку: >= {min_quantity}')

        if max_quantity is not None:
            queryset = queryset.filter(quantity__lte=max_quantity)
            self.stdout.write(f'📦 Фильтр по остатку: <= {max_quantity}')

        if name_filter:
            queryset = queryset.filter(product__name__icontains=name_filter)
            self.stdout.write(f'🔍 Фильтр по названию: {name_filter}')

        if warehouse_filter:
            queryset = queryset.filter(warehouse_location__icontains=warehouse_filter)
            self.stdout.write(f'🏭 Фильтр по складу: {warehouse_filter}')

        count = queryset.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('⚠️ Нет товаров для экспорта'))
            return

        self.stdout.write(f'📊 Найдено товаров для экспорта: {count}')

        # Если формат django - используем стандартный сериализатор
        if format_type == 'django':
            data = serializers.serialize('json', queryset, indent=2,
                                         use_natural_foreign_keys=True)

            # Добавляем метаинформацию
            export_data = {
                'export_date': timezone.now().isoformat(),
                'total_items': count,
                'format': 'django',
                'data': json.loads(data)
            }
        else:
            # Формируем данные для экспорта
            export_data = {
                'export_date': timezone.now().isoformat(),
                'total_items': count,
                'format': format_type,
                'filters': {
                    'category': category_filter,
                    'min_quantity': min_quantity,
                    'max_quantity': max_quantity,
                    'name': name_filter,
                    'warehouse': warehouse_filter,
                },
                'data': []
            }

            for item in queryset:
                # Получаем имя категории
                category_name = item.product.category.name if item.product.category else None

                if format_type == 'full':
                    # Полный экспорт
                    export_data['data'].append({
                        'product': {
                            'id': item.product.id,
                            'name': item.product.name,
                            'description': item.product.description,
                            'price': float(item.product.price),
                            'category': category_name,
                            'discount': item.product.discount,
                            'quantity': item.product.quantity,
                            'created_at': item.product.created_at.isoformat() if hasattr(item.product,
                                                                                         'created_at') and item.product.created_at else None,
                            'updated_at': item.product.updated_at.isoformat() if hasattr(item.product,
                                                                                         'updated_at') and item.product.updated_at else None,
                        },
                        'inventory': {
                            'id': item.id,
                            'quantity': item.quantity,
                            'reserved_quantity': item.reserved_quantity,
                            'available_quantity': item.available_quantity,
                            'warehouse_location': item.warehouse_location,
                            'last_restocked_date': item.last_restocked_date.isoformat() if item.last_restocked_date else None,
                            'created_at': item.created_at.isoformat() if item.created_at else None,
                            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                        }
                    })

                elif format_type == 'detailed':
                    # Детальный экспорт
                    export_data['data'].append({
                        'product_name': item.product.name,
                        'category': category_name,
                        'price': float(item.product.price),
                        'discount': item.product.discount,
                        'quantity': item.quantity,
                        'reserved_quantity': item.reserved_quantity,
                        'available_quantity': item.available_quantity,
                        'warehouse_location': item.warehouse_location,
                        'last_restocked_date': item.last_restocked_date.isoformat() if item.last_restocked_date else None,
                    })

                else:  # simple
                    # Простой экспорт
                    export_data['data'].append({
                        'product_name': item.product.name,
                        'category': category_name,
                        'quantity': item.quantity,
                        'reserved_quantity': item.reserved_quantity,
                        'available_quantity': item.available_quantity,
                        'warehouse_location': item.warehouse_location,
                    })

        # Сохраняем в файл
        try:
            # Создаем директорию если ее нет
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            file_size = os.path.getsize(file_path)
            self.stdout.write('=' * 70)
            self.stdout.write(self.style.SUCCESS(f'✅ Данные успешно экспортированы'))
            self.stdout.write(f'📁 Файл: {file_path}')
            self.stdout.write(f'📏 Размер: {file_size} байт ({file_size / 1024:.2f} КБ)')
            self.stdout.write(f'📊 Записей: {len(export_data["data"])}')
            self.stdout.write('=' * 70)

        except Exception as e:
            raise CommandError(f'Ошибка при сохранении файла: {e}')