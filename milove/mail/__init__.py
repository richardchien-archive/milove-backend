from django.core.mail import EmailMessage


def send_mail(subject='', html='', from_email=None,
              to=None, cc=None, bcc=None, fail_silently=False):
    msg = EmailMessage(subject=subject, body=html, from_email=from_email,
                       to=to, cc=cc, bcc=bcc)
    msg.content_subtype = 'html'
    msg.send(fail_silently=fail_silently)
