from django.template.loader import render_to_string

from .thread_pool import async_run
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
