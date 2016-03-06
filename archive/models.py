from django.db import models


class PermaFolder(models.Model):
    folder_id = models.BigIntegerField(primary_key=True)
    opinion = models.ForeignKey('opinions.Opinion')
