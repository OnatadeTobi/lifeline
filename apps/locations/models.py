from django.db import models

# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            # For fast lookups by name (case-insensitive searches in future)
            models.Index(fields=['name'], name='state_name_idx'),
        ]

    def __str__(self):
        return self.name
    

class LocalGovernment(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='local_governments', db_index=True)
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'name']
        indexes = [
            # For cascading dropdowns: getting all LGAs for a state, alphabetically
            models.Index(fields=['state', 'name'], name='lga_state_name_idx'),
        ]

    def __str__(self):
        return f"{self.name}, {self.state.code}"