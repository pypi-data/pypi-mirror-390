from django.db import models

from .member import Member
from .utils import TimesStampMixin


class Feedback(TimesStampMixin):

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)
    comments = models.TextField()
