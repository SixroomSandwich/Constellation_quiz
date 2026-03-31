from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from .models import Constellation
from .forms import ConstellationForm

def home(request):
    return render(request, 'quiz/home.html')

def constellation_list(request):
    '''Страница со списком всех созвездий'''
    constellations = Constellation.objects.all()
    return render(request, 'quiz/constellation_list.html', {
        'constellations': constellations
    })

def constellation_detail(request, pk):
    '''Страница с детальной информацией о созвездии'''
    constellation = get_object_or_404(Constellation, pk=pk)
    return render(request, 'quiz/constellation_detail.html', {
        'constellation': constellation
    })

def constellation_create(request):
    '''Страница добавления нового созвездия'''
    if request.method == 'POST':
        form = ConstellationForm(request.POST)
        if form.is_valid():
            constellation = form.save()
            messages.success(request, f'Созвездие "{constellation.name_ru}" успешно добавлено!')
            return redirect('constellation_detail', pk=constellation.pk)
    else:
        form = ConstellationForm

    return render(request, 'quiz/constellation_form.html', {
        'form': form,
        'title': 'Добавить созвездие',
        'button_text': 'Добавить'
    })

def constellation_edit(request, pk):
    '''Страница редактирования созвездия'''
    constellation = get_object_or_404(Constellation, pk=pk)

    if request.method == 'POST':
        form = ConstellationForm(request.POST, instance=constellation)
        if form.is_valid():
            constellation = form.save()
            messages.success(request, f'Созвездие "{constellation.name_ru}" успешно обновлено!')
            return redirect('constellation_detail', pk=constellation.pk)
    else:
        form = ConstellationForm(instance=constellation)

    return render(request, 'quiz/constellation_form.html', {
        'form': form,
        'title': 'Редактировать созвездие',
        'button_text': 'Сохранить',
        'constellation': constellation
    })

def constellation_delete(request, pk):
    '''Страница удаления созвездия'''
    constellation = get_object_or_404(Constellation, pk=pk)
    
    if request.method == 'POST':
        name = constellation.name_ru
        constellation.delete()
        messages.success(request, f'Созвездие "{name}" удалено')
        return redirect('constellation_list')
    
    return render(request, 'quiz/constellation_confirm_delete.html', {
        'constellation': constellation
    })
