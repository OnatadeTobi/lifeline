from django.db import models

# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    

class LocalGovernment(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='local_governments')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'name']

    def __str__(self):
        return f"{self.name}, {self.state.code}"