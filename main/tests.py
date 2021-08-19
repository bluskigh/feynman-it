from django.test import TestCase, Client
from django.db.models import Q
from django.contrib.auth.models import Permission

from .models import User, Note, Folder

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
        response = self.client.post('/new_note/', content_type='application/json', data={'title': 'Testing note'})
        self.assertTrue(Note.objects.count())
        self.assertEqual(response.status_code, 200)
    

    def test_edit_note(self):
        """Test editing note"""
        self.test_add_note()

        print('>>>>>>>>>>>>>>Editing note')

        print('>>>>Before editing')
        note = Note.objects.get(title='Testing note')
        print(note.more_information())
        # The way I have it done is the data is sent as a JSON string where once the to_python() coerces the value back to a data type it knows to load the dumped json text
        response = self.client.post(f'/notes/{note.id}/edit/', data={'title': 'Edited testing note', 
            'step_one_iterations': dumps({'added': ['Some random text.', 'Another random text', 'With commas,,,yes']}), 
            'step_two_iterations': '',
            'links': dumps({'1': ['1', 'First link title', 'google.com']}),
            'step_three': '', 'understand': '' })

        print('>>>>After first edit')
        note = Note.objects.get(title='Edited testing note')
        print(note.more_information())
        response = self.client.post(f'/notes/{note.id}/edit/', data={'title': 'Edited testing note', 
            'step_one_iterations': dumps({'edit': {'1': 'Edited some random text'}}),
            'step_two_iterations': dumps({'added': ['Second iteration first']}),
            'links': '', 'step_three': 'Final step should be loaded', 'understand': True })

        print('>>>>After second edit')
        note = Note.objects.get(title='Edited testing note')
        print(note.more_information())
        # note still same, not modified
        self.assertEqual(len(note.step_one_iterations), 3)
        self.assertEqual(note.step_one_iterations[0], 'Edited some random text')


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
