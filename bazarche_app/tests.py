from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Category, Tag
from django.contrib.auth.models import User

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name_fa='دسته تست')
        self.product = Product.objects.create(
            name_fa='محصول تست',
            category=self.category,
            city='کابل',
            seller_contact='09123456789',
            is_approved=True
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), 'محصول تست')

class ProductListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name_fa='دسته تست')
        for i in range(15):
            Product.objects.create(
                name_fa=f'محصول {i}',
                category=self.category,
                city='کابل',
                seller_contact='09123456789',
                is_approved=True
            )

    def test_product_list_status_code(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        response = self.client.get(reverse('product_list'))
        self.assertTrue('products' in response.context)
        self.assertEqual(len(response.context['products']), 9)  # page size

    def test_ajax_pagination(self):
        response = self.client.get(reverse('product_list'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertIn('has_next', response.json())

class ProductRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name_fa='دسته تست')

    def test_register_product_get(self):
        response = self.client.get(reverse('register_product'))
        self.assertEqual(response.status_code, 200)

    def test_register_product_post_valid(self):
        data = {
            'name': 'محصول جدید',
            'description': 'توضیحات محصول',
            'category': self.category.id,
            'city': 'کابل',
            'price': 1000,
            'discount_price': 900,
            'is_featured': False,
            'is_discounted': True,
            'seller_contact': '09123456789',
            'tags': [],
        }
        response = self.client.post(reverse('register_product'), data)
        # Since images are required, this should fail and render form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لطفا حداقل یک عکس برای محصول خود آپلود کنید.")

class AdminAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.client.login(username='admin', password='pass')

    def test_manage_products_access(self):
        response = self.client.get(reverse('manage_products'))
        self.assertEqual(response.status_code, 200)

    def test_manage_categories_access(self):
        response = self.client.get(reverse('manage_categories'))
        self.assertEqual(response.status_code, 200)
