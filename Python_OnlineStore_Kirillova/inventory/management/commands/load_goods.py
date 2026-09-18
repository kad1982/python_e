import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from products.models import Product, Category  # Добавили импорт Category
from ...models import Inventory


class Command(BaseCommand):
    help = 'Загрузка товаров и остатков из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Путь к JSON файлу с данными',
            default='fixtures/inventory_data.json'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить таблицы перед загрузкой'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Обновить существующие товары'
        )
        parser.add_argument(
            '--create-products',
            action='store_true',
            help='Создавать товары, если их нет в базе'
        )
        parser.add_argument(
            '--create-categories',
            action='store_true',
            help='Создавать категории, если их нет в базе'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_existing = options['clear']
        update_existing = options['update']
        create_products = options['create_products']
        create_categories = options.get('create_categories', False)

        # Проверяем существование файла
        if not os.path.exists(file_path):
            raise CommandError(f'Файл "{file_path}" не найден!')

        # Загружаем данные из JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Ошибка парсинга JSON: {e}')

        # Проверяем формат данных
        if not isinstance(data, list):
            raise CommandError('Данные должны быть в формате списка объектов')

        # Очищаем таблицы если нужно
        if clear_existing:
            self.stdout.write('Очистка таблиц...')
            with transaction.atomic():
                Inventory.objects.all().delete()
                if create_products:
                    # Очищаем все
                    Product.objects.all().delete()
                    if create_categories:
                        Category.objects.all().delete()

        # Статистика
        stats = {
            'products_created': 0,
            'products_updated': 0,
            'inventory_created': 0,
            'inventory_updated': 0,
            'categories_created': 0,
            'errors': 0,
            'skipped': 0
        }
        errors = []

        # Кэш для категорий
        category_cache = {}

        self.stdout.write(f'Начинаем загрузку {len(data)} товаров...')

        for idx, item in enumerate(data, 1):
            try:
                # Проверяем обязательные поля
                # Поддерживаем оба варианта: 'name' и 'product_name'
                product_name = item.get('name') or item.get('product_name')

                if not product_name:
                    errors.append(f"Строка {idx}: Пропущено название товара")
                    stats['errors'] += 1
                    continue

                # Получаем или создаем категорию
                category = None
                category_name = item.get('category')

                if category_name:
                    if category_name in category_cache:
                        category = category_cache[category_name]
                    else:
                        try:
                            category = Category.objects.get(name=category_name)
                            category_cache[category_name] = category
                        except Category.DoesNotExist:
                            if create_categories:
                                # Создаем новую категорию
                                category = Category.objects.create(
                                    name=category_name,
                                    description=f"Категория {category_name}"
                                )
                                category_cache[category_name] = category
                                stats['categories_created'] += 1
                                self.stdout.write(self.style.SUCCESS(f'Создана категория: {category_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f'Категория "{category_name}" не найдена. Товар будет без категории.'
                                ))

                # Поиск или создание товара
                try:
                    # Пытаемся найти товар по имени
                    product = Product.objects.get(name=product_name)
                    product_created = False

                    # Обновляем товар если нужно
                    if update_existing:
                        product.description = item.get('product_description') or item.get('description',
                                                                                          product.description)
                        product.price = item.get('selling_price') or item.get('price', product.price)
                        if category:
                            product.category = category
                        product.discount = item.get('discount', product.discount)
                        product.quantity = item.get('quantity', product.quantity)
                        product.save()
                        stats['products_updated'] += 1

                except Product.DoesNotExist:
                    if not create_products:
                        self.stdout.write(self.style.WARNING(
                            f'Товар "{product_name}" не найден. Пропускаем...'
                        ))
                        stats['skipped'] += 1
                        continue

                    # Создаем новый товар
                    product = Product.objects.create(
                        name=product_name,
                        description=item.get('product_description') or item.get('description', ''),
                        price=item.get('selling_price') or item.get('price', 0),
                        category=category if category else Category.objects.first(),  # Если категории нет, берем первую
                        discount=item.get('discount', 0),
                        quantity=item.get('quantity', 0),
                    )
                    stats['products_created'] += 1
                    product_created = True

                # Создаем или обновляем запись в инвентаре
                inventory, created = Inventory.objects.get_or_create(
                    product=product,
                    defaults={
                        'quantity': item.get('quantity', 0),
                        'reserved_quantity': item.get('reserved_quantity', 0),
                        'warehouse_location': item.get('warehouse_location', 'Основной склад'),
                        'last_restocked_date': timezone.now(),
                    }
                )

                if not created and update_existing:
                    inventory.quantity = item.get('quantity', inventory.quantity)
                    inventory.reserved_quantity = item.get('reserved_quantity', inventory.reserved_quantity)
                    inventory.warehouse_location = item.get('warehouse_location', inventory.warehouse_location)
                    inventory.last_restocked_date = timezone.now()
                    inventory.save()
                    stats['inventory_updated'] += 1
                elif created:
                    stats['inventory_created'] += 1

                # Прогресс
                if idx % 10 == 0:
                    self.stdout.write(f'Обработано: {idx} товаров...')

            except ValidationError as e:
                stats['errors'] += 1
                errors.append(
                    f"Строка {idx} ({product_name if 'product_name' in locals() else 'unknown'}): Ошибка валидации - {e}")
            except Exception as e:
                stats['errors'] += 1
                errors.append(f"Строка {idx} ({product_name if 'product_name' in locals() else 'unknown'}): {str(e)}")

        # Вывод результатов
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 РЕЗУЛЬТАТЫ ЗАГРУЗКИ'))
        self.stdout.write('=' * 70)
        if stats['categories_created'] > 0:
            self.stdout.write(f'✅ Категорий создано: {stats["categories_created"]}')
        self.stdout.write(f'✅ Товаров создано: {stats["products_created"]}')
        self.stdout.write(f'✅ Товаров обновлено: {stats["products_updated"]}')
        self.stdout.write(f'✅ Записей инвентаря создано: {stats["inventory_created"]}')
        self.stdout.write(f'✅ Записей инвентаря обновлено: {stats["inventory_updated"]}')
        self.stdout.write(f'⏭️ Пропущено: {stats["skipped"]}')

        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f'❌ Ошибок: {stats["errors"]}'))
            if errors:
                self.stdout.write('\n'.join(errors[:10]))
                if len(errors) > 10:
                    self.stdout.write(f'... и еще {len(errors) - 10} ошибок')
        self.stdout.write('=' * 70)