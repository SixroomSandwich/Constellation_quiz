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
    all_constellations = list(Constellation.objects.all())
    
    # Если созвездий меньше 2, викторина не работает
    if len(all_constellations) < 2:
        messages.warning(request, 'Добавьте хотя бы 2 созвездия для викторины!')
        return redirect('constellation_list')
    
    # Инициализируем сессию для викторины
    if 'quiz_remaining' not in request.session:
        # Создаём перемешанный список ID всех созвездий
        all_ids = [c.id for c in all_constellations]
        random.shuffle(all_ids)
        request.session['quiz_remaining'] = all_ids
        request.session['quiz_completed'] = []
        request.session['quiz_score'] = 0
        messages.info(request, 'Начинаем викторину! Всего вопросов: ' + str(len(all_constellations)))
    
    # Получаем текущий вопрос
    remaining = request.session.get('quiz_remaining', [])
    
    # Если все вопросы пройдены
    if len(remaining) == 0:
        total = len(request.session.get('quiz_completed', []))
        score = request.session.get('quiz_score', 0)
        
        # Показываем результат
        messages.success(request, f'Викторина завершена! Твой результат: {score} из {total} ({int(score/total*100)}%)')
        
        # Очищаем сессию
        request.session.pop('quiz_remaining', None)
        request.session.pop('quiz_completed', None)
        request.session.pop('quiz_score', None)
        
        return render(request, 'quiz/quiz_complete.html', {
            'score': score,
            'total': total,
            'percentage': int(score/total*100) if total > 0 else 0
        })
    
    # Берём следующий вопрос
    current_id = remaining[0]
    current = get_object_or_404(Constellation, pk=current_id)
    
    # Получаем варианты ответов (3 других случайных созвездия)
    other_constellations = [c for c in all_constellations if c.id != current_id]
    sample_size = min(3, len(other_constellations))
    options = random.sample(other_constellations, sample_size)
    answer_options = options + [current]
    random.shuffle(answer_options)
    
    # Сохраняем правильный ответ
    request.session['current_question_id'] = current_id
    
    # Получаем статистику
    completed = len(request.session.get('quiz_completed', []))
    total = len(all_constellations)
    score = request.session.get('quiz_score', 0)
    
    return render(request, 'quiz/quiz_question.html', {
        'constellation': current,
        'options': answer_options,
        'current_number': completed + 1,
        'total_questions': total,
        'score': score,
        'progress_percent': int((completed + 1) / total * 100),
    })
    

def quiz_check(request):
    '''Проверка ответа пользователя'''
    if request.method != 'POST':
        return redirect('quiz_question')
    
    selected_id = request.POST.get('selected_id')
    current_id = request.session.get('current_question_id')
    remaining = request.session.get('quiz_remaining', [])
    
    if not selected_id or not current_id or not remaining:
        return redirect('quiz_question')
    
    try:
        selected = Constellation.objects.get(pk=selected_id)
        current = Constellation.objects.get(pk=current_id)
        is_correct = (int(selected_id) == int(current_id))
    except Constellation.DoesNotExist:
        return redirect('quiz_question')
    
    # Обновляем статистику
    if is_correct:
        request.session['quiz_score'] = request.session.get('quiz_score', 0) + 1
        messages.success(request, f'Правильно! {selected.name_ru} - верный ответ!')
    else:
        messages.error(request, f'Неправильно! Правильный ответ: {current.name_ru}!')
    
    # Перемещаем текущий вопрос из remaining в completed
    if remaining and remaining[0] == current_id:
        remaining.pop(0)
        request.session['quiz_remaining'] = remaining
        
        completed = request.session.get('quiz_completed', [])
        completed.append(current_id)
        request.session['quiz_completed'] = completed
    
    # Удаляем временный ключ
    if 'current_question_id' in request.session:
        del request.session['current_question_id']
    
    return redirect('quiz_question')

def quiz_reset(request):
    '''Сброс прогресса викторины'''
    request.session.pop('quiz_remaining', None)
    request.session.pop('quiz_completed', None)
    request.session.pop('quiz_score', None)
    request.session.pop('current_question_id', None)
    
    messages.info(request, 'Прогресс викторины сброшен!')
    return redirect('quiz_question')