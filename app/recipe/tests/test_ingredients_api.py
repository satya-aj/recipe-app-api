from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    "Test the publicly available ingredients API"
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        "Test theat login is required"
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PriveteIngredientsApiTests(TestCase):
    "Test the provate Ingredients API"
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retreive_ingredient_list(self):
        "test retrieving a list of ingredients"
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Sale")

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        "Test that ingredients for the authentication user are required"
        user2 = get_user_model().objects.create_user(
            'other@test.com'
            'testpass'
        )
        Ingredient.objects.create(user=user2, name="Vaniger")
        ingredient = Ingredient.objects.create(user=self.user, name='Turmic')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
