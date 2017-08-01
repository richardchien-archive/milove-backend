from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from .thread_pool import async_run
from .auth import User
from ..mail import send_mail


def async_send_mail(subject, html, to):
    if isinstance(to, str) and to:
        to = [to]
    if not to:
        return
    async_run(send_mail, subject=subject, html=html, to=to, fail_silently=True)


def notify_signed_up(user):
    async_send_mail(subject='注册成功',
                    html=render_to_string('shop/mails/signed_up.html',
                                          context=locals()),
                    to=[user.email])


def notify_reset_password(user, token):
    async_send_mail(subject='重置密码',
                    html=render_to_string('shop/mails/reset_password.html',
                                          context=locals()),
                    to=[user.email])


def notify_order_created(order):
    try:
        async_send_mail(subject='订单创建成功',
                        html=render_to_string(
                            'shop/mails/order_created.html',
                            context=locals()),
                        to=[order.user.email])
    except TemplateDoesNotExist:
        pass

    staffs = User.objects.filter(
        groups__name=settings.ORDER_NOTIFICATION_GROUP_NAME)
    try:
        async_send_mail(subject='有新的订单',
                        html=render_to_string(
                            'shop/mails/order_created_staff.html',
                            context=locals()
                        ),
                        to=[staff.email for staff in staffs])
    except TemplateDoesNotExist:
        pass


def notify_order_status_changed(order):
    status = order.status.replace('-', '_')
    try:
        async_send_mail(subject='订单状态变更',
                        html=render_to_string(
                            'shop/mails/order_%s.html' % status,
                            context=locals()),
                        to=[order.user.email])
    except TemplateDoesNotExist:
        pass

    staffs = User.objects.filter(
        groups__name=settings.ORDER_NOTIFICATION_GROUP_NAME)
    try:
        async_send_mail(subject='订单#%s状态变更为%s' % (order.pk, order.status),
                        html=render_to_string(
                            'shop/mails/order_%s_staff.html' % status,
                            context=locals()
                        ),
                        to=[staff.email for staff in staffs])
    except TemplateDoesNotExist:
        pass
