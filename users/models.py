from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """can_be_contacted (BooleanField): Indique le consentement de l'utilisateur à être
            contacté. Si `True`, l'utilisateur accepte de recevoir des communications.
        can_data_be_shared (BooleanField): Indique le consentement de l'utilisateur
            concernant le partage de ses données. Si `True`, l'utilisateur accepte
            que ses données puissent être partagées avec des tiers."""
    age = models.PositiveIntegerField(blank=True, null=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
