from django.test import SimpleTestCase, Client
from django.urls import reverse, resolve
from elearn.views import sign_up, sign_in


class TestAuthUrls(SimpleTestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_signup_url(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, sign_up)

    def test_signin_url(self):
        url = reverse('signin')
        self.assertEquals(resolve(url).func, sign_in)


