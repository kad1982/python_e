from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Listing
from .forms import ListingForm


class ListingListView(ListView):
    """Список всех не созданных мною объявлений (с фильтрацией по категориям)"""
    model = Listing
    template_name = 'listing/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12  # Пагинация по 12 штук на страницу

    def get_queryset(self):
        queryset = Listing.objects.exclude(author=self.request.user).filter(
            status=Listing.ListingStatus.PUBLISHED
        ).order_by('-created_at')

        # Фильтрация по категории (если передана в GET-запросе)
        category_name = self.request.GET.get('category')
        if category_name and category_name != 'all':
            queryset = queryset.filter(categories__name__iexact=category_name)

        return queryset


class MyListingListView(ListView):
    """Список моих объявлений"""
    model = Listing
    template_name = 'listing/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12  # Пагинация по 12 штук на страницу

    def get_queryset(self):
        queryset = Listing.objects.filter(author=self.request.user).order_by('-created_at')

        # Фильтрация по категории (если передана в GET-запросе)
        category_name = self.request.GET.get('category')
        if category_name and category_name != 'all':
            queryset = queryset.filter(categories__name__iexact=category_name)

        return queryset


class ListingDetailView(DetailView):
    """Детальная страница объявления"""
    model = Listing
    template_name = 'listing/listing_detail.html'
    context_object_name = 'listing'


class ListingCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления (только для авторизованных)"""
    model = Listing
    form_class = ListingForm
    template_name = 'listing/listing_form.html'
    success_url = reverse_lazy('listing:my_listing_list')

    def form_valid(self, form):
        # Автоматически привязываем автора к текущему пользователю
        form.instance.author = self.request.user
        return super().form_valid(form)


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование объявления (только автор)"""
    model = Listing
    form_class = ListingForm
    template_name = 'listing/listing_form.html'

    def test_func(self):
        # Проверяем, что редактирует именно автор
        listing = self.get_object()
        return self.request.user == listing.author

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
