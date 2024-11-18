from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, SupportTicket


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(
            username='testuser',
            password='Test@1234',
            first_name='Иван',
            last_name='Иванов',
            email='testuser@example.com',
            phone='89997778855',
            role_name='Client'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.password,'Test@1234')
        self.assertEqual(user.role_name, 'Client')
        print("Тест создания пользователя пройден")


class SupportTicketModelTest(TestCase):
    def test_create_support_ticket(self):
        user = User.objects.create(
            username='clientuser',
            password='Client@1234',
            first_name='Ольга',
            last_name='Петрова',
            email='clientuser@example.com',
            phone='89995554433',
            role_name='Client'
        )
        ticket = SupportTicket.objects.create(
            issue_description='Описание проблемы с аккаунтом.',
            answer_status='Ожидание',
            client_id=user
        )
        self.assertEqual(ticket.issue_description, 'Описание проблемы с аккаунтом.')
        self.assertEqual(ticket.client_id.username, 'clientuser')
        print("Тест создания обращения в поддержку пройден")


class PhoneValidatorTest(TestCase):
    def test_phone_validation(self):
        user = User(
            username='invaliduser',
            password='Test@1234',
            first_name='Тест',
            last_name='Тестов',
            email='invaliduser@example.com',
            phone='8123456789'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
        print("Тест валидации номера телефона пройден")