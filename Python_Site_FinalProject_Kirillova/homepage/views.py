from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'in_development.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - О нас'
        context['content'] = "О нас"
        context['text_on_page'] = "Текст о том почему этот магазин такой классный, и какой хороший товар."
        return context


class IndexView(TemplateView):
    template_name = 'homepage/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Главная'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class HowItWorksView(TemplateView):
    template_name = 'homepage/how_it_works.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Как это работает'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class DeliveryView(TemplateView):
    template_name = 'homepage/delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Доставка и возврат'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class SizesView(TemplateView):
    template_name = 'homepage/sizes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Размерная сетка'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class TermsView(TemplateView):
    template_name = 'homepage/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Условия аренды'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class FaqView(TemplateView):
    template_name = 'homepage/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Вопросы и ответы'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class PrivacyView(TemplateView):
    template_name = 'homepage/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Политика конфиденциальности'
        context['content'] = "Магазин аренды одежды HOME"
        return context

class UserAgreementView(TemplateView):
    template_name = 'homepage/user_agreement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home - Пользовательское соглашение'
        context['content'] = "Магазин аренды одежды HOME"
        return context

