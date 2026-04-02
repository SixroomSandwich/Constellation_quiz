from django import forms
from .models import Constellation

class ConstellationForm(forms.ModelForm):
    class Meta:
        model = Constellation
        fields = ['name_ru', 'name_la', 'description', 'image_url']
        labels = {
            'name_ru': 'Название (рус.)',
            'name_la': 'Название (лат.)',
            'description': 'Описание',
            'image_url': 'Ссылка на изображение',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def clean_name_ru(self):
        '''Проверка: название не должно быть пустым и не должно дублироваться'''
        name = self.cleaned_data.get('name_ru')
        if not name:
            raise forms.ValidationError('Название обязятельно для заполнения')
        
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if Constellation.objects.exclude(pk=instance.pk).filter(name_ru=name).exists():
                raise forms.ValidationError('Созвездие с таким названием уже существует')
        else:
            if Constellation.objects.filter(name_ru=name).exists():
                raise forms.ValidationError('Созвездие с таким названием уже существует')
            
        return name
    
    def clean_image_url(self):
        '''Проверка: URL должен быть корректным'''
        url = self.cleaned_data.get('image_url')
        if url and not url.startswith('http'):
            raise forms.ValidationError('Введите корректный URL (должен начинаться с http:// или https://)')
        return url
    