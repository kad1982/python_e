from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from listing.models import Listing, Category
from rental_request.models import RentalRequest
from datetime import date, timedelta
import logging

# Настройка логгера для записи тестов
logger = logging.getLogger(__name__)
logging.basicConfig(filename='tests/test_app.log', level=logging.DEBUG)

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс с общими данными для тестов"""

    def setUp(self):
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.ru',
            password='password123',
            phone='+79991234567'
        )
        # Создаем второго пользователя (продавца)
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.ru',
            password='password123',
            phone='+79997654321'
        )
        # Создаем модератора (админа)
        self.moderator = User.objects.create_superuser(
            username='admin',
            email='admin@test.ru',
            password='password123'
        )

        # Создаем категорию
        self.category = Category.objects.create(name='Вечерние платья')

        # Создаем тестовое объявление (опубликованное)
        self.listing = Listing.objects.create(
            title='Красное платье',
            description='Красивое платье для выпускного',
            price=1500.00,
            location='Москва',
            available_from=date.today(),
            available_to=date.today() + timedelta(days=10),
            author=self.seller,
            contact_phone='+79991234567',
            contact_email='seller@test.ru',
            status=Listing.ListingStatus.PUBLISHED
        )
        self.listing.categories.add(self.category)


class AuthTests(BaseTestCase):
    """Тесты аутентификации (регистрация, вход)"""

    def test_registration(self):
        """Тест: успешная регистрация нового пользователя"""
        logger.debug("Запуск теста регистрации")
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@test.ru',
            'password1': 'SuperSecret123',
            'password2': 'SuperSecret123',
            'phone': '+79990001122',
            'last_name': 'Иванов',
            'first_name': 'Иван'
        })
        # Проверяем, что редирект прошел успешно (302) и пользователь создан
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        logger.info("Регистрация прошла успешно")

    def test_login(self):
        """Тест: успешный вход в систему"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после входа
        # Проверяем, что пользователь авторизован
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class ListingTests(BaseTestCase):
    """Тесты для объявлений (создание, поиск, просмотр)"""

    def test_create_listing(self):
        """Тест: создание нового объявления (статус должен быть Черновик)"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('listing:listing_create'), {
            'title': 'Новое платье',
            'description': 'Описание нового платья',
            'price': 2000,
            'location': 'Санкт-Петербург',
            'available_from': date.today(),
            'available_to': date.today() + timedelta(days=5),
            'contact_phone': '+79991234567',
            'contact_email': 'test@test.ru',
            'status': Listing.ListingStatus.DRAFT
        })
        self.assertEqual(response.status_code, 302)  # Успешный редирект
        new_listing = Listing.objects.get(title='Новое платье')
        # Проверяем, что статус по умолчанию - Черновик (0)
        self.assertEqual(new_listing.status, Listing.ListingStatus.DRAFT)
        self.assertEqual(new_listing.author, self.user)

    def test_search_by_keyword(self):
        """Тест: поиск объявлений по ключевому слову"""
        response = self.client.get(reverse('listing:listing_list'), {'q': 'Красное'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Красное платье')
        self.assertNotContains(response, 'Синее платье')

    def test_search_by_price(self):
        """Тест: поиск объявлений по максимальной цене"""
        # Ищем вещи дешевле 1000 рублей (наше платье стоит 1500)
        response = self.client.get(reverse('listing:listing_list'), {'max_price': '1000'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Красное платье')

        # Ищем вещи дешевле 2000 рублей
        response = self.client.get(reverse('listing:listing_list'), {'max_price': '2000'})
        self.assertContains(response, 'Красное платье')

    def test_listing_detail_view(self):
        """Тест: открытие страницы объявления"""
        response = self.client.get(reverse('listing:listing_detail', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listing/listing_detail.html')


class ModerationTests(BaseTestCase):
    """Тесты для модерации объявлений"""

    def test_moderator_can_approve(self):
        """Тест: модератор может одобрить объявление"""
        # Создаем объявление на модерации
        pending_listing = Listing.objects.create(
            title='На модерации',
            description='Ждет проверки',
            price=1000,
            location='Москва',
            available_from=date.today(),
            available_to=date.today() + timedelta(days=5),
            author=self.seller,
            contact_phone='+79991234567',
            contact_email='test@test.ru',
            status=Listing.ListingStatus.PENDING
        )

        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('moderation:approve', kwargs={'pk': pending_listing.pk}))

        self.assertEqual(response.status_code, 302)  # Редирект
        pending_listing.refresh_from_db()  # Обновляем данные из БД
        self.assertEqual(pending_listing.status, Listing.ListingStatus.PUBLISHED)

    def test_regular_user_cannot_approve(self):
        """Тест: обычный пользователь не может одобрить объявление"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('moderation:approve', kwargs={'pk': self.listing.pk}))

        # Ожидаем 403 Forbidden, так как срабатывает UserPassesTestMixin
        self.assertEqual(response.status_code, 403)


class RentalRequestTests(BaseTestCase):
    """Тесты для запросов на аренду и транзакций"""

    def test_create_rental_request(self):
        """Тест: создание запроса на аренду"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('rental_request:create_request', kwargs={'listing_pk': self.listing.pk}), {
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today() + timedelta(days=3),
            'quantity': 1,
            'comment': 'Хочу арендовать'
        })

        self.assertEqual(response.status_code, 302)  # Редирект на "Мои запросы"
        self.assertTrue(RentalRequest.objects.filter(renter=self.user, listing=self.listing).exists())
        logger.info("Запрос на аренду успешно создан")

    def test_cannot_rent_own_listing(self):
        """Тест: продавец не может арендовать свою же вещь"""
        self.client.login(username='seller', password='password123')
        # Пытаемся отправить запрос на свое же объявление
        response = self.client.get(reverse('rental_request:create_request', kwargs={'listing_pk': self.listing.pk}))

        # В вашей вьюхе при попытке арендовать свою вещь должен быть редирект
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RentalRequest.objects.filter(renter=self.seller, listing=self.listing).exists())