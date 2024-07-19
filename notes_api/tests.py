from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Note

from .models import User, Note
# Create your tests here.

User = get_user_model()

class NotesApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.notes_url = reverse('notes_list')
        self.search_url = reverse('search_notes')
        
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.save()

        # Authenticate user
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data.get('access')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Create a note
        self.note = Note.objects.create(user=self.user, title='Test Note', content='This is a test note.')
        self.note.save()

    def test_signup(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_login(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_create_note(self):
        data = {
            'title': 'New Note',
            'content': 'This is a new note.',
            'user': self.user.id 
        }
        response = self.client.post(self.notes_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)
    
    def test_get_notes(self):
        response = self.client.get(self.notes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_note_by_id(self):
        url = reverse('note_detail', kwargs={'id': self.note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')

    def test_update_note(self):
        url = reverse('note_detail', kwargs={'id': self.note.id})
        data = {
            'title': 'Updated Note',
            'content': 'This is an updated note.',
            'user': self.user.id 
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.content, 'This is an updated note.')

    def test_delete_note(self):
        url = reverse('note_detail', kwargs={'id': self.note.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_share_note(self):
        # share_url = reverse('share_note', kwargs={'id': self.note.id}, format='json')
        new_user = User.objects.create_user(username='shareduser', password='sharedpassword')
        data = {
            'username': [new_user.id]
        }
        response = self.client.post(reverse('share_note', kwargs={'id': self.note.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertIn(new_user, self.note.shared_with.all())

    def test_search_notes(self):
        search_url = f"{self.search_url}?q=Test"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Note')
