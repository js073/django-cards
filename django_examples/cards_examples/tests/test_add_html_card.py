import re

from cards.standard import CardMixin
from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView


class _CsrfCardView(CardMixin, TemplateView):
    """Minimal view that renders an HTML card containing a {% csrf_token %}."""

    def build_card(self):
        return self.add_html_card(
            card_name='csrf_probe',
            title='CSRF probe',
            context_template_name='cards_examples/csrf_probe.html',
        )


def _card_html(view):
    """Return the rendered html stored on the HTML card."""
    card = view.build_card()
    return card.extra_card_info.get('html') or ''


class TestAddHtmlCardCsrf(TestCase):
    """add_html_card must render with a RequestContext so {% csrf_token %} emits
    a token. Without it, POST forms inside HTML cards fail CSRF with a 403."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_csrf_token_rendered_when_request_present(self):
        view = _CsrfCardView()
        view.request = self.factory.get('/')
        html = _card_html(view)
        tokens = re.findall(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
        self.assertTrue(tokens, 'add_html_card should emit a csrf token when a request is set')
        self.assertTrue(tokens[0], 'csrf token value should be non-empty')

    def test_no_request_does_not_crash(self):
        # Views without a request (rare) must still render, just without a token.
        view = _CsrfCardView()
        html = _card_html(view)
        self.assertIn('<form', html)
