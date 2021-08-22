from django.test import TestCase, Client
from django.db.models import Q
from django.contrib.auth.models import Permission
from django.shortcuts import reverse

from .models import User, Note, Folder, Iteration, Link

from json import dumps, loads


class TestApp(TestCase):
    def setUp(self):
        # build rows
        self.client = Client()


    def test_register(self):
        """Testing registering a user"""
        response = self.client.post('/accounts/register/', data={'username': 'mario', 'password': 'mario', 'confirmation': 'mario', 'email': 'mario@gmail.com'})
        self.assertEqual(User.objects.filter(username='mario').count(), 1)
        # redirection only occurs when successfuly registered therefore being redirected to login page
        self.assertEqual(response.status_code, 302)
        

    def test_login(self):
        """Testing logging in registered user"""
        self.test_register()
        response = self.client.post('/accounts/login/', data={'username': 'mario', 'password': 'mario'})
        user = User.objects.get(username='mario')

        # another way to test the user was logged in is to check his permissions, each login checks if user has certain permissions, if not they are added
        # since this user was just created he should have them added in previous post request
        note_query = Q(codename__contains='_note')
        folder_query = Q(codename__contains='_folder')
        permissions = Permission.objects.filter(note_query & folder_query)
        self.assertTrue(user.has_perms([p.codename for p in permissions]))

        # redirection only occurs when successfuly registered therefore being redirected to index route
        self.assertEqual(response.status_code, 302)


    def test_add_note(self):
        """Test the creation of a note"""
        self.test_login()
        response = self.client.post(reverse('new_note'), content_type='application/json', data={'title': 'Testing note'})
        self.assertTrue(Note.objects.count())
        self.assertEqual(response.status_code, 200)
    

    def test_add_iteration(self, which=1, title='First iteration'):
        """Test adding an iteration to notes. Default adds to step one"""
        self.test_add_note()
        note = Note.objects.get(title='Testing note')
        response = self.client.post(reverse('iterations'), content_type='application/json', data={'title': title, 'text': 'This is the text of the iteration', 'noteid': note.id, 'which': which})
        iteration = Iteration.objects.get(title=title)
        self.assertTrue(iteration)
        note = Note.objects.get(title='Testing note')
        if which == 1:
            self.assertEqual(note.step_one_iterations.count(), 1)
        elif which == 2:
            self.assertEqual(note.step_two_iterations.count(), 1)

    def test_add_step_one_iteration(self):
        """Test adding iteration to step_two"""
        self.test_add_iteration(which=2, title='Second iteration')


    def test_add_link(self):
        """Test add link to iteration"""
        self.test_add_iteration()
        note = Note.objects.get(title='Testing note')
        iteration = note.step_one_iterations.get(title='First iteration')
        response = self.client.post(reverse('links'), content_type='application/json', data={'title': 'First link', 'href': 'https://cs50.com', 'which': iteration.id, 'noteid': note.id})

        iteration = note.step_one_iterations.get(title='First iteration')
        self.assertTrue(Link.objects.get(title='First link'))
        self.assertEqual(iteration.links.count(), 1)

    def test_general_link(self):
        """Test adding a general link"""
        self.test_add_note()
        note = Note.objects.get(title='Testing note')
        response = self.client.post(reverse('links'), content_type='application/json', data={'title': 'General link', 'href': 'https://cs50.com', 'which': 0, 'noteid': note.id})
        note = Note.objects.get(title='Testing note')
        self.assertTrue(note.general_links)
        self.assertEqual(note.general_links.count(), 1)

    def test_delete_link(self):
        """Test delete link and compare length of note links"""
        self.test_add_link()
        link = Link.objects.get(title='First link')
        response = self.client.delete(reverse('link', kwargs={'id': link.id}))
        iteration = Iteration.objects.get(title='First iteration')
        self.assertEqual(iteration.links.count(), 0)

    def test_edit_link(self):
        """Test editing a link, only update title and not href"""
        self.test_add_link()
        link = Link.objects.get(title='First link')
        response = self.client.patch(reverse('link', kwargs={'id': link.id}), content_type='application/json', data={'title': 'First link edited', 'href': None})
        link = Link.objects.get(title='First link edited')
        self.assertTrue(link)
        self.assertEqual(link.href, 'https://cs50.com')


    def test_add_folder(self):
        """Testing the creation of a folder"""
        self.test_login()
        response = self.client.post('/new_folder/', data={'title': 'New folder'})
        self.assertTrue(Folder.objects.get(title='New folder'))


    def test_move_notes_to_folder(self):
        self.test_add_folder()
        self.test_add_note()
        folder = Folder.objects.get(title='New folder')
        note = Note.objects.get(title='Testing note')
        # moving note to folder viewing
        response = self.client.post(f'/folders/{folder.id}/', data={'available_notes': [note.id]})
        # asserting the length of notes in the folder is 1 since we just moved a note into the folder
        self.assertEqual(folder.folder_notes.count(), 1)
        self.assertEqual(response.status_code, 302)


    def test_clear_folder(self):
        """Testing clearing a folder, first adding note to folder then deleting folder"""
        self.test_move_notes_to_folder()
        folder = Folder.objects.get(title='New folder')
        response = self.client.post(f'/folders/{folder.id}/delete/')
        folder = Folder.objects.get(title='New folder')
        self.assertEqual(folder.folder_notes.count(), 0)


    def test_delete_folder(self):
        """Testing deleting a folder after it has been cleared"""
        self.test_clear_folder()
        folder = Folder.objects.get(title='New folder')
        response = self.client.post(f'/folders/{folder.id}/delete/')
        try:
            folder = Folder.objects.get(title='New folder')
        except:
            self.assertEqual(Folder.objects.count(), 2)
