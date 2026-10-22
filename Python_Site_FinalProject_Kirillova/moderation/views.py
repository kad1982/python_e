from django.views.generic import ListView, View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from listing.models import Listing

class ModeratorRequiredMixin(UserPassesTestMixin):
    """Миксин, проверяющий, что пользователь - модератор или админ"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class PendingListingsView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    """Список объявлений, ожидающих модерации"""
    model = Listing
    template_name = 'moderation/pending_list.html'
    context_object_name = 'listings'
    paginate_by = 20

    def get_queryset(self):
        # Показываем только те, что на модерации
        return Listing.objects.filter(status=Listing.ListingStatus.PENDING).order_by('created_at')

class ApproveListingView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    """Одобрение объявления"""
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        listing.status = Listing.ListingStatus.PUBLISHED
        listing.save()
        messages.success(request, f'Объявление "{listing.title}" одобрено.')
        return redirect('moderation:pending_list')

class RejectListingView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    """Отклонение объявления"""
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        listing.status = Listing.ListingStatus.REJECTED
        listing.save()
        messages.warning(request, f'Объявление "{listing.title}" отклонено.')
        return redirect('moderation:pending_list')