from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from .forms import TaskCreationForm
from .models import Task
from django.contrib.auth.decorators import login_required, permission_required
# Create your views here.


def signup(request):
    error_DB = ""
    error = ""
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try: # Everything is ok
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                print("Usuario creado")
                login(request, user)
                return redirect('home')
            except IntegrityError: # Problem while creating user
                error_DB = 'El usuario ya existe'
        else: # Passwords don't match
            error = 'Las contraseñas no coinciden'
    # Normal request
    return render(request,'auth/index.html', {
        'form': UserCreationForm,
        'error_DB': error_DB,
        'error': error,
    })

def home(request):
    return render(request, 'home.html')


@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    error = ""
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], 
        password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Usuario o contraseña incorrectos'
    return render(request,'auth/login.html', {
        'form': AuthenticationForm,
        'error': error,
    })


@login_required
@permission_required('tasks.add_task')
def createTask(request):
    error = ""
    if request.method == 'POST':
        try:
            form = TaskCreationForm(request.POST)
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasksView')
        except IntegrityError:
            error = 'The task already exists'
        except ValueError:
            error = 'Pleasse, provide valid data'
    
    return render(request,'tasks/create.html', {
        'form': TaskCreationForm,
        'error': error,
    })

@login_required
@permission_required('tasks.view_task')
def tasksView(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'tasks/show.html', {
        'tasks': tasks,
    })

@login_required
@permission_required('tasks.view_task')
def taskDetailsView(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    error = ""
    form = TaskCreationForm(instance=task)
    if request.method == 'POST':
        try:
            form = TaskCreationForm(request.POST, instance=task)
            form.save()
            return redirect('tasksView')
        except:
            error = 'Pleasse, introduce valid data'
            
    return render(request, 'tasks/detail.html', {
        'form': form,
        'task': task,
        'error': error,
    })

@login_required
@permission_required('tasks.change_task')
def taskCompleted(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect('tasksView')
    
@login_required
@permission_required('tasks.delete_task')
def deleteTask(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.delete()
    return redirect('tasksView')

@login_required
@permission_required('tasks.change_task')
def completedTasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=False)
    return render(request, 'tasks/completed.html', {
        'tasks': tasks,
    })
