import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aio_pika
import aiosmtplib

from core.config import settings

log = logging.getLogger(__name__)


async def produce_message(text: str) -> bool:
    try:
        connection = await aio_pika.connect_robust(
            host=settings.RMQ_HOST,
            port=settings.RMQ_PORT,
            login=settings.RMQ_USER,
            password=settings.RMQ_PASSWORD,
        )
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=text.encode()),
                routing_key=settings.MQ_ROUTING_KEY,
            )
        return True
    except Exception as e:
        log.error(f"Failed to produce message: {e}")
        return False


async def process_new_message(
    ch,
    method,
    properties,
    body,
) -> None:
    try:
        data = json.loads(body.decode())
        email = data.get("email")
        token = data.get("token")

        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_FROM
        msg["To"] = email
        msg["Subject"] = "Token for account reset"

        msg.attach(
            MIMEText(
                f"""Here is token for deleting your account: 
                "
                {token}
                "
                thanks for using our service!""",
                "plain",
            )
        )

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.MAIL_FROM,
            password=settings.APP_PASSWORD_SECRET,
            use_tls=True,
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
