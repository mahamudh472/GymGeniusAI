from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from io import BytesIO
from PIL import Image
from accounts.models import User
from nutrition.models import TemporaryMealUpload, UserUploadedMeal

def generate_valid_image():
    file_obj = BytesIO()
    image = Image.new("RGB", (1, 1), color="red")
    image.save(file_obj, "jpeg")
    file_obj.seek(0)
    return SimpleUploadedFile("meal.jpg", file_obj.read(), content_type="image/jpeg")

class NutritionViewsTests(APITestCase):
    def setUp(self):
        # Create active verified user
        self.user = User.objects.create_user(
            email="nutritionuser@example.com",
            password="password123",
            full_name="Nutrition User",
            is_verified=True,
            daily_calorie_target=2000.0
        )
        
        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "nutritionuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # URLs
        self.home_url = reverse('nutrition-home')
        self.upload_meal_url = reverse('upload-meal')
        self.save_meal_url = reverse('save-meal-upload')

    def test_nutrition_home_empty(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_meals'], 0)
        self.assertEqual(response.data['streak'], 0)
        self.assertEqual(response.data['calories_target'], 2000.0)

    @patch('nutrition.views.analyze_single_meal')
    def test_upload_meal_success(self, mock_analyze):
        mock_analyze.return_value = {
            'meal_name': 'Chicken Rice',
            'estimated_calories': 450,
            'overall_health_insight': 'Good balance of protein and carbs.',
            'macronutrients': {'protein_g': 35, 'carbs_g': 50, 'fat_g': 10},
            'micronutrients': {'iron_mg': 3, 'calcium_mg': 50},
            'improvement_suggestion': 'Add some greens.'
        }

        image = generate_valid_image()
        payload = {'image': image}
        response = self.client.post(self.upload_meal_url, payload)
        if response.status_code != status.HTTP_201_CREATED:
            print("UPLOAD ERROR:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('temp_upload_id', response.data)
        self.assertEqual(response.data['analysis_data']['meal_name'], 'Chicken Rice')

        # Verify TemporaryMealUpload is created
        self.assertTrue(TemporaryMealUpload.objects.filter(user=self.user).exists())

    @patch('nutrition.views.analyze_single_meal')
    def test_save_meal_upload_success(self, mock_analyze):
        mock_analyze.return_value = {
            'meal_name': 'Steak Salad',
            'estimated_calories': 500,
            'overall_health_insight': 'High protein.',
            'macronutrients': {'protein_g': 40, 'carbs_g': 15, 'fat_g': 25},
            'micronutrients': {'iron_mg': 4},
            'improvement_suggestion': 'Less dressing.'
        }

        # First, upload the image
        image = generate_valid_image()
        payload = {'image': image}
        upload_response = self.client.post(self.upload_meal_url, payload)
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        temp_id = upload_response.data['temp_upload_id']

        # Now, save it
        save_payload = {'temp_upload_id': temp_id}
        save_response = self.client.post(self.save_meal_url, save_payload, format='json')
        self.assertEqual(save_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(save_response.data['meal_name'], 'Steak Salad')
        self.assertEqual(save_response.data['estimated_calories'], 500)

        # Verify UserUploadedMeal is saved and TemporaryMealUpload is deleted
        self.assertTrue(UserUploadedMeal.objects.filter(user=self.user, meal_name='Steak Salad').exists())
        self.assertFalse(TemporaryMealUpload.objects.filter(id=temp_id).exists())

    def test_save_meal_upload_not_found(self):
        save_payload = {'temp_upload_id': 99999}
        response = self.client.post(self.save_meal_url, save_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
