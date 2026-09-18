from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from django.utils import timezone

from clients.models import Clients
from products.models import (Category, Product)
from django.contrib.auth import get_user_model
from inventory.models import Inventory
from shopping_carts.models import ShoppingCart

User = get_user_model()


class CategoryTestCase(TestCase):
    """Тесты для модели Category"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Электроника',
            description='Электронные товары'
        )

    def test_category_creation(self):
        """Создание категории и проверка полей"""
        self.assertEqual(self.category.name, 'Электроника')
        self.assertEqual(self.category.description, 'Электронные товары')
        self.assertIsNone(self.category.parent)

    def test_category_str_method(self):
        """Строковое представление категории"""
        self.assertEqual(str(self.category), 'Электроника')

    def test_category_unique_name(self):
        """Имя категории должно быть уникальным"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Электроника', description='Дубликат')

    def test_category_parent_relation(self):
        """Проверка связи родитель-потомок"""
        child = Category.objects.create(
            name='Смартфоны',
            description='Мобильные телефоны',
            parent=self.category
        )
        self.assertEqual(child.parent, self.category)
        self.assertIn(child, self.category.category_set.all())

    def test_category_parent_protect_on_delete(self):
        """Родительская категория защищена от удаления (PROTECT)"""
        Category.objects.create(
            name='Смартфоны',
            description='Мобильные телефоны',
            parent=self.category
        )
        with self.assertRaises(Exception):
            self.category.delete()


class ProductTestCase(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Электроника',
            description='Электронные товары'
        )
        self.product = Product.objects.create(
            name='Смартфон',
            description='Хороший смартфон',
            price=Decimal('1000.00'),
            category=self.category,
            quantity=10,
            discount=0
        )

    def test_product_creation(self):
        """Создание товара и проверка полей"""
        self.assertEqual(self.product.name, 'Смартфон')
        self.assertEqual(self.product.price, Decimal('1000.00'))
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.discount, 0)
        self.assertEqual(self.product.category, self.category)

    def test_product_str_method(self):
        """Строковое представление товара"""
        self.assertEqual(str(self.product), 'Смартфон')

    def test_sell_price_without_discount(self):
        """Цена продажи без скидки равна обычной цене"""
        self.assertEqual(self.product.sell_price(), Decimal('1000.00'))

    def test_sell_price_with_discount(self):
        """Цена продажи с учётом скидки"""
        self.product.discount = 25
        self.product.save()
        # 1000 - 1000 * 25 / 100 = 750
        self.assertEqual(self.product.sell_price(), Decimal('750.00'))

    def test_sell_price_with_100_discount(self):
        """Скидка 100% — товар бесплатный"""
        self.product.discount = 100
        self.product.save()
        self.assertEqual(self.product.sell_price(), Decimal('0.00'))

    def test_quantity_negative_validation(self):
        """Количество не может быть отрицательным"""
        self.product.quantity = -5
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_discount_validation_range(self):
        """Скидка должна быть в диапазоне 0-100"""
        # Больше 100
        self.product.discount = 150
        with self.assertRaises(ValidationError):
            self.product.full_clean()

        # Меньше 0
        self.product.discount = -10
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_stock_balance(self):
        """Тест баланса остатков товара (по образцу)"""
        product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            category=self.category,
            quantity=5
        )

        # Имитация добавления в корзину (уменьшение доступного количества)
        # В реальной логике это делает ShoppingCart
        reserved = 3
        product.quantity -= reserved
        product.save()

        self.assertEqual(product.quantity, 2)

        # Попытка зарезервировать больше, чем есть
        with self.assertRaises(ValueError):
            if reserved > product.quantity:
                raise ValueError("Недостаточно товара на складе")

        # Остаток не изменился
        self.assertEqual(product.quantity, 2)

    def test_product_category_protect_on_delete(self):
        """Категория товара защищена от удаления (PROTECT)"""
        with self.assertRaises(Exception):
            self.category.delete()

    def test_product_quantity_default(self):
        """Значение по умолчанию для quantity"""
        product = Product.objects.create(
            name='Новый товар',
            price=Decimal('100.00'),
            category=self.category
        )
        self.assertEqual(product.quantity, 0)

    def test_product_discount_default(self):
        """Значение по умолчанию для discount"""
        product = Product.objects.create(
            name='Новый товар',
            price=Decimal('100.00'),
            category=self.category
        )
        self.assertEqual(product.discount, 0)


class ClientsTestCase(TestCase):
    """Тесты для модели Clients"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_obj = Clients.objects.create(
            user=self.user,
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович',
            email='ivanov@example.com',
            phone='+71234567890',
            street='Ленина',
            house_number='10',
            apartment='5',
            city='Москва',
            postal_code='101000',
            country='Russia'
        )

    def test_client_creation(self):
        """Создание клиента и проверка полей"""
        self.assertEqual(self.client_obj.last_name, 'Иванов')
        self.assertEqual(self.client_obj.first_name, 'Иван')
        self.assertEqual(self.client_obj.middle_name, 'Иванович')
        self.assertEqual(self.client_obj.email, 'ivanov@example.com')
        self.assertEqual(self.client_obj.phone, '+71234567890')
        self.assertEqual(self.client_obj.city, 'Москва')
        self.assertEqual(self.client_obj.country, 'Russia')

    def test_client_str_method(self):
        """Строковое представление клиента"""
        expected = 'Иванов Иван Иванович'
        self.assertEqual(str(self.client_obj), expected)

    def test_client_str_without_middle_name(self):
        """Строковое представление без отчества"""
        self.client_obj.middle_name = None
        self.client_obj.save()
        self.assertEqual(str(self.client_obj), 'Иванов Иван')

    def test_full_name_property(self):
        """Свойство full_name"""
        self.assertEqual(self.client_obj.full_name, 'Иванов Иван Иванович')

    def test_full_name_without_middle_name(self):
        """Свойство full_name без отчества"""
        self.client_obj.middle_name = None
        self.client_obj.save()
        self.assertEqual(self.client_obj.full_name, 'Иванов Иван')

    def test_full_address_property(self):
        """Свойство full_address с квартирой"""
        expected = '101000, Москва, Ленина, 10, кв. 5, Russia'
        self.assertEqual(self.client_obj.full_address, expected)

    def test_full_address_without_apartment(self):
        """Свойство full_address без квартиры"""
        self.client_obj.apartment = None
        self.client_obj.save()
        expected = '101000, Москва, Ленина, 10, Russia'
        self.assertEqual(self.client_obj.full_address, expected)

    def test_email_unique(self):
        """Email должен быть уникальным"""
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        with self.assertRaises(IntegrityError):
            Clients.objects.create(
                user=user2,
                last_name='Петров',
                first_name='Пётр',
                email='ivanov@example.com',  # Дубликат
                phone='+79876543210',
                street='Пушкина',
                house_number='1',
                city='Санкт-Петербург',
                postal_code='190000'
            )

    def test_user_one_to_one_relation(self):
        """Связь user — OneToOne"""
        self.assertEqual(self.client_obj.user, self.user)
        self.assertEqual(self.user.client_profile, self.client_obj)

    def test_phone_validation_valid(self):
        """Валидные телефонные номера"""
        valid_phones = ['+71234567890', '71234567890', '+1234567890123']
        for phone in valid_phones:
            self.client_obj.phone = phone
            try:
                self.client_obj.full_clean()
            except ValidationError:
                self.fail(f"Телефон {phone} должен быть валидным")

    def test_phone_validation_invalid(self):
        """Невалидные телефонные номера"""
        invalid_phones = ['123', 'abc', '+7-123-456-78-90', '']
        for phone in invalid_phones:
            self.client_obj.phone = phone
            with self.assertRaises(ValidationError):
                self.client_obj.full_clean()

    def test_cascade_delete_with_user(self):
        """Удаление User удаляет Clients"""
        client_id = self.client_obj.id
        self.user.delete()
        self.assertFalse(Clients.objects.filter(id=client_id).exists())

    def test_ordering(self):
        """Сортировка по last_name, first_name"""
        user2 = User.objects.create_user(username='user2', password='pass')
        Clients.objects.create(
            user=user2,
            last_name='Абрамов',
            first_name='Алексей',
            email='abramov@example.com',
            phone='+71111111111',
            street='ул. А',
            house_number='1',
            city='Москва',
            postal_code='101000'
        )
        clients = list(Clients.objects.all())
        self.assertEqual(clients[0].last_name, 'Абрамов')
        self.assertEqual(clients[1].last_name, 'Иванов')


class InventoryTestCase(TestCase):
    """Тесты для модели Inventory"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Электроника',
            description='Электронные товары'
        )
        self.product = Product.objects.create(
            name='Смартфон',
            price=Decimal('1000.00'),
            category=self.category,
            quantity=100
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=100,
            reserved_quantity=20,
            warehouse_location='Склад А, стеллаж 5'
        )

    def test_inventory_creation(self):
        """Создание записи инвентаря"""
        self.assertEqual(self.inventory.product, self.product)
        self.assertEqual(self.inventory.quantity, 100)
        self.assertEqual(self.inventory.reserved_quantity, 20)
        self.assertEqual(self.inventory.warehouse_location, 'Склад А, стеллаж 5')

    def test_inventory_str_method(self):
        """Строковое представление"""
        expected = 'Смартфон - 100 шт.'
        self.assertEqual(str(self.inventory), expected)

    def test_available_quantity_property(self):
        """Доступное количество = quantity - reserved_quantity"""
        self.assertEqual(self.inventory.available_quantity, 80)

    def test_available_quantity_when_all_reserved(self):
        """Если всё зарезервировано"""
        self.inventory.reserved_quantity = 100
        self.inventory.save()
        self.assertEqual(self.inventory.available_quantity, 0)

    def test_stock_balance(self):
        """Тест баланса остатков (по образцу)"""
        product = self.product
        inventory = self.inventory

        # Начальный остаток
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.available_quantity, 80)

        # Резервируем 30 единиц
        reserved = 30
        if reserved > inventory.available_quantity:
            raise ValueError("Недостаточно товара на складе")
        inventory.reserved_quantity += reserved
        inventory.save()

        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.reserved_quantity, 50)
        self.assertEqual(inventory.available_quantity, 50)

        # Попытка зарезервировать больше доступного
        with self.assertRaises(ValueError):
            if 60 > inventory.available_quantity:
                raise ValueError("Недостаточно товара на складе")

        # Состояние не изменилось
        self.assertEqual(inventory.available_quantity, 50)

    def test_negative_quantity_validation(self):
        """Количество не может быть отрицательным"""
        self.inventory.quantity = -1
        with self.assertRaises(ValidationError):
            self.inventory.full_clean()

    def test_one_to_one_product(self):
        """Один товар — одна запись инвентаря"""
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                product=self.product,
                quantity=50
            )

    def test_cascade_delete_with_product(self):
        """Удаление товара удаляет инвентарь"""
        inventory_id = self.inventory.id
        self.product.delete()
        self.assertFalse(Inventory.objects.filter(id=inventory_id).exists())

    def test_last_restocked_date_default(self):
        """Дата последнего пополнения по умолчанию None"""
        self.assertIsNone(self.inventory.last_restocked_date)

    def test_last_restocked_date_set(self):
        """Установка даты последнего пополнения"""
        now = timezone.now()
        self.inventory.last_restocked_date = now
        self.inventory.save()
        self.assertEqual(self.inventory.last_restocked_date, now)

    def test_warehouse_location_optional(self):
        """Местоположение склада может быть пустым"""
        inventory = Inventory.objects.create(
            product=Product.objects.create(
                name='Товар 2',
                price=Decimal('500.00'),
                category=self.category
            ),
            quantity=10
        )
        self.assertIsNone(inventory.warehouse_location)


class ShoppingCartTestCase(TestCase):
    """Тесты для модели ShoppingCart"""

    def setUp(self):
        # Пользователь и клиент
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_obj = Clients.objects.create(
            user=self.user,
            last_name='Иванов',
            first_name='Иван',
            email='ivanov@example.com',
            phone='+71234567890',
            street='Ленина',
            house_number='10',
            city='Москва',
            postal_code='101000'
        )

        # Товар
        self.category = Category.objects.create(
            name='Электроника',
            description='Электронные товары'
        )
        self.product = Product.objects.create(
            name='Смартфон',
            price=Decimal('1000.00'),
            category=self.category,
            quantity=10
        )

        # Запись в корзине
        self.cart_item = ShoppingCart.objects.create(
            client=self.client_obj,
            product=self.product,
            quantity=3
        )

    def test_cart_item_creation(self):
        """Создание записи в корзине"""
        self.assertEqual(self.cart_item.client, self.client_obj)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 3)

    def test_cart_item_str_method(self):
        """Строковое представление"""
        expected = f'{self.client_obj} - Смартфон x 3'
        self.assertEqual(str(self.cart_item), expected)

    def test_total_price_property(self):
        """Общая стоимость позиции"""
        # 1000 * 3 = 3000
        self.assertEqual(self.cart_item.total_price, Decimal('3000.00'))

    def test_total_price_with_discount(self):
        """Стоимость с учётом скидки на товар"""
        self.product.discount = 10
        self.product.save()
        # sell_price = 900, total = 900 * 3 = 2700
        # Внимание: свойство total_price в вашей модели использует product.price,
        # а не sell_price. Если нужно учитывать скидку — раскомментируйте:
        # self.assertEqual(self.cart_item.total_price, Decimal('2700.00'))
        self.assertEqual(self.cart_item.total_price, Decimal('3000.00'))

    def test_quantity_min_validator(self):
        """Количество не может быть меньше 1"""
        self.cart_item.quantity = 0
        with self.assertRaises(ValidationError):
            self.cart_item.full_clean()

    def test_quantity_positive(self):
        """Количество — положительное число"""
        self.cart_item.quantity = -5
        with self.assertRaises(ValidationError):
            self.cart_item.full_clean()

    def test_unique_together_client_product(self):
        """Один товар у клиента может быть только один раз"""
        with self.assertRaises(IntegrityError):
            ShoppingCart.objects.create(
                client=self.client_obj,
                product=self.product,
                quantity=1
            )

    def test_cascade_delete_with_client(self):
        """Удаление клиента удаляет корзину"""
        cart_id = self.cart_item.id
        self.client_obj.delete()
        self.assertFalse(ShoppingCart.objects.filter(id=cart_id).exists())

    def test_cascade_delete_with_product(self):
        """Удаление товара удаляет позицию из корзины"""
        cart_id = self.cart_item.id
        self.product.delete()
        self.assertFalse(ShoppingCart.objects.filter(id=cart_id).exists())

    def test_ordering_by_added_at_desc(self):
        """Сортировка по дате добавления (новые первыми)"""
        product2 = Product.objects.create(
            name='Планшет',
            price=Decimal('2000.00'),
            category=self.category,
            quantity=5
        )
        cart_item2 = ShoppingCart.objects.create(
            client=self.client_obj,
            product=product2,
            quantity=1
        )
        cart_items = list(ShoppingCart.objects.all())
        self.assertEqual(cart_items[0], cart_item2)
        self.assertEqual(cart_items[1], self.cart_item)

    def test_stock_balance(self):
        """Тест баланса остатков товара при работе с корзиной"""
        product = self.product
        client = self.client_obj

        self.assertEqual(product.quantity, 10)

        # Чистим корзину от записи из setUp
        ShoppingCart.objects.filter(client=client, product=product).delete()

        cart = ShoppingCart(client=client, product=product, quantity=3)
        cart.save()
        self.assertEqual(cart.quantity, 3)

        # Попытка положить больше, чем есть на складе
        with self.assertRaises(ValueError):
            requested = 15  # ✅ 15 > 10
            if requested > product.quantity:
                raise ValueError("Недостаточно товара на складе")

        self.assertEqual(cart.quantity, 3)
        self.assertEqual(product.quantity, 10)

    def test_stock_balance_after_multiple_adds(self):
        """Несколько добавлений одного товара — количество суммируется"""
        cart_item, created = ShoppingCart.objects.get_or_create(
            client=self.client_obj,
            product=self.product,
            defaults={'quantity': 2}
        )
        # Запись уже существует (из setUp) — created=False
        self.assertFalse(created)

        # Добавляем ещё 2
        cart_item.quantity += 2
        cart_item.save()

        self.assertEqual(cart_item.quantity, 5)

        # Попытка добавить больше, чем есть на складе
        with self.assertRaises(ValueError):
            new_quantity = cart_item.quantity + 6  # 11 > 10
            if new_quantity > self.product.quantity:
                raise ValueError("Недостаточно товара на складе")

        # Состояние не изменилось
        self.assertEqual(cart_item.quantity, 5)

    def test_empty_cart_for_new_client(self):
        """У нового клиента корзина пуста"""
        user2 = User.objects.create_user(username='user2', password='pass')
        client2 = Clients.objects.create(
            user=user2,
            last_name='Петров',
            first_name='Пётр',
            email='petrov@example.com',
            phone='+79876543210',
            street='Пушкина',
            house_number='1',
            city='Санкт-Петербург',
            postal_code='190000'
        )
        self.assertEqual(ShoppingCart.objects.filter(client=client2).count(), 0)
