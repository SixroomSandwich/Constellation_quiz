from django.db import models

class Constellation(models.Model):
    # Названия созвездий на русском и на латыни
    name_ru = models.CharField(max_length=100, verbose_name="Название (рус.)")
    name_la = models.CharField(max_length=100, verbose_name="Название (лат.)", blank=True)

    # Информация о созвездии
    description = models.TextField(verbose_name="Описание", blank=True)

    # Картинка созвездия
    image_url = models.URLField(verbose_name="Ссылка на созвездие", blank=True)

    # Мета-информация
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name_ru
    
    class Meta:
        verbose_name = "Созвездие"
        verbose_name_plural = "созвездия"
        ordering = ['name_ru']
        