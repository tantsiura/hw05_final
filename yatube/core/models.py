from django.db import models


class Pub_date_Model(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date_of_pub',
        db_index=True
    )

    class Meta:
        abstract = True
