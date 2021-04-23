from typing import Any, Dict, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def email_send(
    text_template: str,
    html_template: str,
    data: Dict[str, Any],
    subject: str,
    emails: List[str],
    bcc: bool = False,
) -> EmailMultiAlternatives:
    text, html = get_template(text_template), get_template(html_template)
    text_content, html_content = text.render(data), html.render(data)
    subject = settings.EMAIL_SUBJECT_PREFIX + subject
    if bcc:
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [], headers={}, bcc=emails)
    else:
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, emails, headers={})
    msg.attach_alternative(html_content, "text/html")

    if not settings.DEBUG or settings.FORCE_EMAIL_SEND:
        msg.send()

    return msg
