from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from .models import *
from django.contrib.auth.models import User

@login_required()
def index(request):
    data = {
        'title': 'Главная страница'}
    return render(request, 'index.html', data)

@login_required()
def allOrders(request):
    orders = Order.objects.all()
    data = {
        'title': 'Просмотр всех заявок',
        'orders': orders}
    return render(request, 'allOrders.html', data)

@login_required()
def createOrder(request):
    if request.method == 'GET':
        form = OrderForm()
        data = {
            'title': 'Создание новой заявки',
            'form': form
        }
        return render(request, 'createOrder.html', data)
    elif request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('success')
        else:
            data = {
                'title': 'Создание новой заявки',
                'form': form    
            }
            return render(request, 'createOrder.html', data)

@login_required()
def completeCreateOrder(request):
    data = {
        'title': 'Заяка успешно создана',
        'content_text': 'Ваша заявка успешно создана. Спасибо большое! Отслеживайте статус в разеделе "Мои заявки"'
    }
    return render(request, 'success.html', data)

@login_required()
def resposibleOrder(request):
    if request.method == 'GET':
        orders = Order.objects.filter(response_person=None).all()
        responsibles = User.objects.filter(person=4).all()
        data = {
            'title': 'Назначение ответственного за заявку',
            'orders': orders,
            'responsibles': responsibles
        }
        return render(request, 'responsiblePerson.html', data)
    elif request.method == 'POST':
        order_id = request.POST.get('order-name')
        worker_id = request.POST.get('responsible-name')
        order = Order.objects.filter(id=order_id).update(response_person_id=int(worker_id))
        return JsonResponse({'success': True, 'data': {}})

@login_required()
def completeSendToWorker(request):
    data = {
        'title': 'Заяка успешно направлена рабочему',
        'content_text': 'Ваша заявка успешно направлена рабочему. Ожидайте выполнения!'
    }
    return render(request, 'success.html', data)

@login_required()
def myOrders(request):
    orders = Order.objects.filter(user=request.user)
    data = {
        'title': 'Мои заявки',
        'orders': orders
    }
    return render(request, 'myOrders.html', data)

@login_required()
def infoPanel(request):
    orders_count = Order.objects.count()
    active_count = Order.objects.filter(response_person__isnull=False).count()
    wait_order = Order.objects.filter(response_person__isnull=True).count()
    orders_list = Order.objects.filter(response_person__isnull=False)
    data = {
        'title': 'Информационная панель',
        'orders_count':orders_count,
        'active_count': active_count,
        'wait_order': wait_order,
        'orders_list': orders_list
    }
    return render(request, 'infoPanel.html', data)

@login_required()
def aiChatBot(request):
    data = {
        'title': 'ИИ ассистент',
    }
    return render(request, 'aiChat.html', data)