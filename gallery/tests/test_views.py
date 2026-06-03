from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from io import BytesIO
from PIL import Image
from accounts.models import User
from gallery.models import UserGallery

def generate_valid_image():
    file_obj = BytesIO()
    image = Image.new("RGB", (1, 1), color="blue")
    image.save(file_obj, "jpeg")
    file_obj.seek(0)
    return SimpleUploadedFile("progress.jpg", file_obj.read(), content_type="image/jpeg")

class GalleryViewsTests(APITestCase):
    def setUp(self):
        # Start patching analyze_user_image to avoid Celery task trying to connect to OpenAI
        self.patcher = patch('gallery.tasks.analyze_user_image')
        self.mock_analyze = self.patcher.start()
        self.mock_analyze.return_value = {
            'summary': 'Good progress summary.',
            'image_type': 'front'
        }

        # Create active verified user
        self.user = User.objects.create_user(
            email="galleryuser@example.com",
            password="password123",
            full_name="Gallery User",
            is_verified=True
        )
        
        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "galleryuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a gallery image object
        image_file = generate_valid_image()
        self.gallery_image = UserGallery.objects.create(
            user=self.user,
            image=image_file,
            image_type="front"
        )

        # URLs
        self.gallery_list_url = reverse('gallery-list')
        self.gallery_detail_url = reverse('gallery-detail', kwargs={'pk': self.gallery_image.id})
        self.gallery_dashboard_url = reverse('gallery-dashboard')

    def tearDown(self):
        self.patcher.stop()

    def test_list_gallery_images(self):
        response = self.client.get(self.gallery_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_gallery_image(self):
        new_image = generate_valid_image()
        payload = {
            "image": new_image
        }
        response = self.client.post(self.gallery_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify in database that it was created and AI analysis updated the image_type to "front"
        new_gallery = UserGallery.objects.exclude(id=self.gallery_image.id).first()
        self.assertIsNotNone(new_gallery)
        self.assertEqual(new_gallery.image_type, "front")
        self.assertTrue(new_gallery.ai_detected)

    def test_gallery_image_detail(self):
        response = self.client.get(self.gallery_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['image_type'], "front")

    def test_gallery_dashboard(self):
        response = self.client.get(self.gallery_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_images'], 1)
        self.assertEqual(response.data['consecutive_days_streak'], 1)
