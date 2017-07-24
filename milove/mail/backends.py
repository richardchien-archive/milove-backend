import re
import copy

import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage
from django.conf import settings


class SendGridEmailBackend(BaseEmailBackend):
    @staticmethod
    def _email_message_to_json_payload(email_message):
        assert email_message.to
        # https://sendgrid.com/docs/API_Reference/api_v3.html
        payload = {
            'personalizations': [
                {
                    'to': [{'email': email} for email in email_message.to],
                }
            ],
            'from': {
                'email': email_message.from_email,
                'name': settings.MAIL_FROM_NAME,
            },
            'subject': email_message.subject,
            'content': [
                {
                    'type': 'text/' + email_message.content_subtype,
                    'value': email_message.body,
                }
            ]
        }
        if email_message.cc:
            payload['personalizations'][0]['cc'] = [
                {'email': email} for email in email_message.cc
            ]
        if email_message.bcc:
            payload['personalizations'][0]['bcc'] = [
                {'email': email} for email in email_message.bcc
            ]
        return payload

    def send_messages(self, email_messages):
        success_count = 0
        session = requests.Session()
        session.headers['Authorization'] = 'Bearer {}'.format(
            settings.SENDGRID_API_KEY
        )
        for email_message in email_messages:
            assert isinstance(email_message, EmailMessage)
            if not email_message.to:
                # there is no 'to', so no need to really send it
                success_count += 1
                continue
            payload = self._email_message_to_json_payload(email_message)
            try:
                resp = session.post('https://api.sendgrid.com/v3/mail/send',
                                    json=payload)
                if resp.status_code == 202:
                    # accepted
                    success_count += 1
            except requests.RequestException:
                pass
        return success_count


class SendCloudEmailBackend(BaseEmailBackend):
    @staticmethod
    def _email_message_to_json_payload(email_message):
        assert email_message.to
        # http://sendcloud.sohu.com/doc/email_v2/send_email/
        payload = {
            'apiUser': settings.SENDCLOUD_API_USER,
            'apiKey': settings.SENDCLOUD_API_KEY,
            'from': email_message.from_email,
            'fromName': settings.MAIL_FROM_NAME,
            'to': ';'.join(email_message.to),
            'subject': email_message.subject,
        }

        if email_message.cc:
            payload['cc'] = ';'.join(email_message.cc)
        if email_message.bcc:
            payload['bcc'] = ';'.join(email_message.bcc)

        if email_message.content_subtype == 'html':
            payload['html'] = email_message.body
        else:
            payload['plain'] = email_message.body

        return payload

    def send_messages(self, email_messages):
        success_count = 0
        session = requests.Session()
        for email_message in email_messages:
            assert isinstance(email_message, EmailMessage)
            if not email_message.to:
                # there is no 'to', so no need to really send it
                success_count += 1
                continue
            payload = self._email_message_to_json_payload(email_message)
            try:
                resp = session.post('http://api.sendcloud.net/apiv2/mail/send',
                                    data=payload)
                if resp.status_code == 200 \
                        and resp.json().get('statusCode') == 200:
                    # ok
                    success_count += 1
            except requests.RequestException:
                pass
        return success_count


_china_mailbox_regex = [
    re.compile(r'.*\.cn'),
    re.compile(r'(?:163|126|qq|vip\.qq|sohu|sina|2008\.sina'
               r'|vip\.sina|51uc|21cn|cntv|189|139|tom|360)\.com'),
    re.compile(r'(?:milove|milosale)\.com'),
]


class HybridEmailBackend(BaseEmailBackend):
    @staticmethod
    def _collect_by_mailbox(all_email: list, china: list, non_china: list):
        for email in all_email:
            mailbox = email.rsplit('@', maxsplit=1)[-1]
            if any(map(lambda r: bool(r.match(mailbox)),
                       _china_mailbox_regex)):
                china.append(email)
            else:
                non_china.append(email)

    def send_messages(self, email_messages):
        messages_to_china = []
        messages_to_nonchina = []
        for msg in email_messages:
            assert isinstance(msg, EmailMessage)
            msg_china = copy.deepcopy(msg)
            msg_nonchina = copy.deepcopy(msg)
            msg_china.to = []
            msg_china.cc = []
            msg_china.bcc = []
            msg_nonchina.to = []
            msg_nonchina.cc = []
            msg_nonchina.bcc = []

            self._collect_by_mailbox(msg.to, msg_china.to, msg_nonchina.to)
            self._collect_by_mailbox(msg.cc, msg_china.cc, msg_nonchina.cc)
            self._collect_by_mailbox(msg.bcc, msg_china.bcc, msg_nonchina.bcc)

            if msg_china.to and not msg_nonchina.to:
                # only china mailboxes
                msg_china.cc.extend(msg_nonchina.cc)
                msg_nonchina.cc = []
                msg_china.bcc.extend(msg_nonchina.bcc)
                msg_nonchina.bcc = []
            elif not msg_china.to and msg_nonchina:
                # only non-china mailboxes
                msg_nonchina.cc.extend(msg_china.cc)
                msg_china.cc = []
                msg_nonchina.bcc.extend(msg_china.bcc)
                msg_china.bcc = []

            if msg_china.to:
                messages_to_china.append(msg_china)
            if msg_nonchina.to:
                messages_to_nonchina.append(msg_nonchina)

        success_count = 0
        if messages_to_china:
            success_count += SendCloudEmailBackend(
                fail_silently=self.fail_silently
            ).send_messages(messages_to_china)
        if messages_to_nonchina:
            success_count += SendGridEmailBackend(
                fail_silently=self.fail_silently
            ).send_messages(messages_to_nonchina)
        return success_count
