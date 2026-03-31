from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Constellation

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