from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Listing
from .forms import ListingForm
from django.db.models import Q


class ListingListView(ListView):
    """Список всех не созданных мною объявлений (с фильтрацией по категориям)"""
    model = Listing
    template_name = 'listing/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12  # Пагинация по 12 штук на страницу

    def get_queryset(self):
        queryset = Listing.objects.filter(
            status=Listing.ListingStatus.PUBLISHED
        ).order_by('-created_at')

        # Исключаем свои объявления, ТОЛЬКО если пользователь авторизован
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(author=self.request.user)

        # 1. Поиск по ключевым словам
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        # 2. Поиск по местоположению
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # 3. Поиск по цене
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # 4. Категория
        category_name = self.request.GET.get('category')
        if category_name and category_name != 'all':
            queryset = queryset.filter(categories__name__iexact=category_name)

        return queryset


class MyListingListView(LoginRequiredMixin, ListView):
    """Список моих объявлений"""
    model = Listing
    template_name = 'listing/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12  # Пагинация по 12 штук на страницу

    def get_queryset(self):
        # Показываем только объявления текущего пользователя
        queryset = Listing.objects.filter(author=self.request.user).order_by('-created_at')

        # 1. Поиск по ключевым словам
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        # 2. Поиск по местоположению
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # 3. Поиск по цене
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # 4. Категория
        category_name = self.request.GET.get('category')
        if category_name and category_name != 'all':
            queryset = queryset.filter(categories__name__iexact=category_name)

        return queryset


class ListingDetailView(DetailView):
    """Детальная страница объявления"""
    model = Listing
    template_name = 'listing/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        queryset = Listing.objects.all()
        user = self.request.user

        # Автор видит свои объявления в любом статусе, модератор — все
        if user.is_authenticated:
            if user.is_staff or user.is_superuser:
                return queryset
            return queryset.filter(
                Q(status=Listing.ListingStatus.PUBLISHED) | Q(author=user)
            )

        # Остальным доступны только опубликованные объявления
        return queryset.filter(status=Listing.ListingStatus.PUBLISHED)


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listing/listing_form.html'

    def form_valid(self, form):
        # Привязываем автора
        form.instance.author = self.request.user
        # # Принудительно ставим статус "Черновик"
        # form.instance.status = Listing.ListingStatus.DRAFT

        messages.success(self.request, f'Объявление сохранено со статусом: "{form.instance.get_status_display()}"')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('listing:my_listing_list')


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование объявления (только автор)"""
    model = Listing
    form_class = ListingForm
    template_name = 'listing/listing_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Запоминаем статус до сохранения правок
        self.original_status = obj.status
        return obj

    def test_func(self):
        listing = self.get_object()
        # Редактировать может только автор любое своё объявление
        return self.request.user == listing.author

    def handle_no_permission(self):
        # Если не прошел test_func, показываем сообщение
        messages.error(self.request, "Вы можете редактировать только свои объявления.")
        return redirect('listing:my_listing_list')

    def form_valid(self, form):
        # Правки опубликованного объявления должны пройти модерацию заново
        if self.original_status == Listing.ListingStatus.PUBLISHED:
            form.instance.status = Listing.ListingStatus.PENDING
        response = super().form_valid(form)
        # Если объявление отправлено на модерацию, выводим уведомление
        if self.object.status == Listing.ListingStatus.PENDING:
            messages.success(self.request, 'Объявление отправлено на модерацию.')
        else:
            messages.success(self.request, 'Объявление сохранено.')
        return response

    def get_success_url(self):
        return reverse('listing:listing_detail', kwargs={'pk': self.object.pk})


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление объявления (только автор)"""
    model = Listing
    template_name = 'listing/listing_confirm_delete.html'
    success_url = reverse_lazy('listing:listing_list')

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.author
