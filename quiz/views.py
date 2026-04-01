from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Constellation
from .forms import ConstellationForm
import random

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

def quiz_question(request):
    '''Главная страница викторины или следующий вопрос'''

    # Получаем все созвездия
    constellations = list(Constellation.objects.all())

    # Если созвездий меньше 2, викторина не работает
    if len(constellations) < 2:
        messages.warning(request, 'Добавьте хотя бы 2 созвездия для викторины!')
        return redirect('constellation_list')
    
    # Получаем текущий вопрос из сессии или создаём новый
    current = None
    if 'current_constellation_id' in request.session:
        # Продолжаем текущий вопрос (после неправильного ответа)
        try:
            current = Constellation.objects.get(pk=request.session['current_constellation_id'])
        except Constellation.DoesNotExist:
            # Если вдруг созвездие удалили, удаляем из сессии
            del request.session['current_constellation_id']
    
    if not current:
        # Выбираем случайное созвездие
        current = random.choice(constellations)
        request.session['current_constellation_id'] = current.id

    # Получаем варианты ответов (3 случайных других созвездия + правильный)
    other_constellations = [c for c in constellations if c.id != current.id]
    options = random.sample(other_constellations, min(3, len(other_constellations)))

    # Добавляем правильный ответ и перемешиваем
    answer_options = options + [current]
    random.shuffle(answer_options)

    # Сохраняем правильный ответ в сессии для проверки
    request.session['correct_answer_id'] = current.id

    # Получаем счёт из сессии
    score = request.session.get('score', {'correct': 0, 'total': 0})
    
    return render(request, 'quiz/quiz_question.html', {
        'constellation': current,
        'options': answer_options,
        'total_count': len(constellations),
        'score': score,
    })

    '''
    return render(request, 'quiz/quiz_question_simple.html', {
        'constellation': current,
        'options': answer_options,
        'total_count': len(constellations),
        'score': score,
    })
    '''
    

def quiz_check(request):
    """Проверка ответа пользователя"""
    if request.method != 'POST':
        return redirect('quiz_question')
    
    selected_id = request.POST.get('selected_id')
    correct_id = request.session.get('correct_answer_id')
    current_id = request.session.get('current_constellation_id')
    
    if not selected_id or not correct_id:
        return redirect('quiz_question')
    
    try:
        selected = Constellation.objects.get(pk=selected_id)
        is_correct = (int(selected_id) == int(correct_id))
    except Constellation.DoesNotExist:
        return redirect('quiz_question')
    
    # Сохраняем результат в сессии
    if 'score' not in request.session:
        request.session['score'] = {'correct': 0, 'total': 0}
    
    score = request.session['score']
    score['total'] += 1
    
    if is_correct:
        score['correct'] += 1
        messages.success(request, f'Правильно! {selected.name_ru} - верный ответ!')
        # Удаляем текущий вопрос, чтобы следующий был новым
        if 'current_constellation_id' in request.session:
            del request.session['current_constellation_id']
    else:
        try:
            correct_constellation = Constellation.objects.get(pk=correct_id)
            messages.error(request, f'Неправильно! {selected.name_ru} - неверный ответ!')
        except Constellation.DoesNotExist:
            messages.error(request, f'Неправильно!')
        # Оставляем текущий вопрос для повторной попытки
    
    request.session['score'] = score
    
    return redirect('quiz_question')

def quiz_reset(request):
    """Сброс прогресса викторины"""
    request.session.pop('score', None)
    request.session.pop('current_constellation_id', None)
    request.session.pop('correct_answer_id', None)
    
    messages.info(request, 'Прогресс викторины сброшен! Начинай заново!')
    return redirect('quiz_question')