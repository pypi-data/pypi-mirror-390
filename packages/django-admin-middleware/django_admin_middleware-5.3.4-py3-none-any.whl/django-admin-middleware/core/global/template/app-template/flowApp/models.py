from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone

class Role(models.Model):
    role_name = models.CharField(max_length=150, blank=False)
    
    def __str__(self):
        return self.role_name
    

class Person(models.Model):
    user = models.OneToOneField(User, verbose_name=("пользователи"), on_delete=models.CASCADE)
    role = models.ForeignKey(Role, verbose_name=("Роль"), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь, создавший заявку", on_delete=models.CASCADE, related_name='created_orders')
    order_name = models.CharField(verbose_name="Предмет заявки", max_length=100)
    order_description = models.TextField(verbose_name="Описание заявки")
    order_status = models.BooleanField(verbose_name = "Активная заявка?", default=True)
    created_at = models.DateTimeField(verbose_name = "Дата создания", auto_now=True)
    response_person = models.ForeignKey(User, blank=True, null=True, verbose_name="Ответственный", on_delete=models.CASCADE, related_name='assigned_orders')
    
    class Meta:
        managed = True
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        
    def __str__(self):
        return self.order_name
