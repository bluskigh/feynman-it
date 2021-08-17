from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    pass


class Folder(models.Model):
    title = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')

    def basic_information(self):
        return {'id': self.id, 'title': self.title, 'owner': self.owner, 'notes_length': self.folder_notes.count()}


class Note(models.Model):
    # title of the note
    title = models.CharField(blank=True, max_length=64)
    # step one text(s)
    step_one_iterations = ArrayField(default=list, blank=True, base_field=models.TextField(blank=True))
    # step two text(s)
    step_two_iterations = ArrayField(default=list, blank=True, base_field=models.TextField(blank=True))
    # step three text
    step_three = models.TextField(blank=True)
    # links for step one
    links = ArrayField(default=list, blank=True,
    base_field=ArrayField(default=list,  base_field=models.TextField(blank=True)))
    # links = ArrayField(default=list, blank=True, base_field=models.TextField(blank=True))
    # does user understand new note
    understand = models.BooleanField(default=False)
    # who owns the note
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', default=None)
    # what folder is it in
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_notes', default=None, null=True)

    def basic_information(self):
        return {'id': self.id, 'title': self.title, 'understand': self.understand}


    def format_links(self):
        links = self.links
        if len(links) == 0:
            return {}
        # if the list only has one item then format is: [1, 2, 3] but greater than 1: [[1, 2, 3], [1, 2, 3]]
        # therefore checking for type of first item in list, if its not a list meaning there is one item
        # just return a dictionary of the item instead of looping logic
        if type(links[0]) != type([]):
            # only one item in links return that
            return {links[0]: links}
        result = {}
        for index, link_item in enumerate(self.links):
            forwhich = link_item[0]
            if result.get(forwhich) is None:
                result[forwhich] = [] 
            link_item.append(index)
            result[forwhich].append(link_item)
        keys = list(result.keys())
        for index, key in enumerate(keys):
            for index2 in range(index+1, len(keys)):
                if keys[index] > keys[index2]:
                    temp = key
                    keys[index] = keys[index2]
                    keys[index2] = temp
        return {key: result.get(key) for key in keys}
    

    def more_information(self):
        return {
            'id': self.id, 
            'title': self.title, 
            'iterations_one': self.step_one_iterations,
            'iterations_two': self.step_two_iterations, 
            'step_three': self.step_three,
            'links': self.format_links(), 
            'understand': self.understand, 
            'owner': self.owner}
