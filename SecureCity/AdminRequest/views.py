from django.shortcuts import render, redirect, get_object_or_404


def becomePatrolManager(request):
    return render(request, 'AdminRequest/becomePatrolManager.html')
