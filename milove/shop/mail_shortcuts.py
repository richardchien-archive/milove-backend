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


def _send_ignore_failure(subject, to, template_name, context=None):
    try:
        async_send_mail(
            subject=subject, to=to,
            html=render_to_string(
                template_name=template_name,
                context=context)
        )
    except TemplateDoesNotExist:
        pass


def notify_user_signed_up(user):
    _send_ignore_failure('注册成功', [user.email],
                         'shop/mails/user_signed_up.html',
                         context=locals())


def notify_user_reset_password(user, token):
    _send_ignore_failure('重置密码', [user.email],
                         'shop/mails/user_reset_password.html',
                         context=locals())


def notify_order_created(order):
    _send_ignore_failure('订单创建成功', [order.user.email],
                         'shop/mails/order_created.html',
                         context=locals())

    staffs = User.objects.filter(
        groups__name=settings.ORDER_NOTIFICATION_GROUP_NAME)
    _send_ignore_failure('有新的订单', [staff.email for staff in staffs],
                         'shop/mails/order_created_staff.html',
                         context=locals())


def notify_order_status_changed(order):
    from .models import Payment
    payment = order.payments.filter(
        status=Payment.STATUS_SUCCEEDED).first()

    status = order.status.replace('-', '_')

    _send_ignore_failure('订单状态变更', [order.user.email],
                         'shop/mails/order_%s.html' % status,
                         context=locals())

    staffs = User.objects.filter(
        groups__name=settings.ORDER_NOTIFICATION_GROUP_NAME)
    _send_ignore_failure('订单#%s状态变更为%s' % (order.pk, order.status),
                         [staff.email for staff in staffs],
                         'shop/mails/order_%s_staff.html' % status,
                         context=locals())


def notify_sell_request_created(sell_req):
    _send_ignore_failure('出售请求创建成功', [sell_req.user.email],
                         'shop/mails/sell_request_created.html',
                         context=locals())

    staffs = User.objects.filter(
        groups__name=settings.SELL_REQUEST_NOTIFICATION_GROUP_NAME)
    _send_ignore_failure('有新的出售请求', [staff.email for staff in staffs],
                         'shop/mails/sell_request_created_staff.html',
                         context=locals())


def notify_sell_request_status_changed(sell_req):
    status = sell_req.status.replace('-', '_')

    _send_ignore_failure('出售请求状态变更', [sell_req.user.email],
                         'shop/mails/sell_request_%s.html' % status,
                         context=locals())

    staffs = User.objects.filter(
        groups__name=settings.SELL_REQUEST_NOTIFICATION_GROUP_NAME)
    _send_ignore_failure('出售请求#%s状态变更为%s' % (sell_req.pk,
                                             sell_req.status),
                         [staff.email for staff in staffs],
                         'shop/mails/sell_request_%s_staff.html' % status,
                         context=locals())
