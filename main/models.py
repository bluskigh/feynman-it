from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    pass


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

    def basic_information(self):
        return {'id': self.id, 'title': self.title}


    def format_links(self):
        links = self.links
        if len(links) == 3:
            # only one item in links return that
            return {links[0]: links}
        result = {}
        for index, link_item in enumerate(self.links):
            forwhich = link_item[0]
            if result.get(forwhich) is None:
                result[forwhich] = [] 
            link_item.append(index)
            result[forwhich].append(link_item)
        return result
    

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
