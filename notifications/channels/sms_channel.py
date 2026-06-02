import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(to: str, body: str) -> bool:
    if not to:
        logger.warning("send_sms called with empty 'to' number. Skipped.")
        return False

    if not settings.INFOBIP_API_KEY or not settings.INFOBIP_BASE_URL:
        logger.warning("Infobip credentials not configured. SMS skipped.")
        return False

    try:
        url = f"{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"

        headers = {
            "Authorization": f"App {settings.INFOBIP_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "messages": [
                {
                    "destinations": [{"to": to}],
                    "from": settings.INFOBIP_SENDER,
                    "text": body
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"[sms_channel] SMS sent successfully to: {to}")
            return True
        else:
            logger.error(
                f"[sms_channel] Infobip error sending to {to}: "
                f"{response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"[sms_channel] Unexpected error sending to {to}: {e}")
        return False