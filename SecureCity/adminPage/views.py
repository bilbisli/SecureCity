from django.shortcuts import render

def adminP(request):
    return render(request, 'AdminPage/AdminPage.html')
