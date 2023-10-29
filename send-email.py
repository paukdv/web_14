from dotenv import load_dotenv

from pathlib import Path
import os

import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

load_dotenv()


class EmailSchema(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME=os.environ['MAIL_USERNAME'],
    MAIL_PASSWORD=os.environ['MAIL_PASSWORD'],
    MAIL_FROM=os.environ['MAIL_FROM'],
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

app = FastAPI()


@app.post("/send-email")
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    """
    The send_in_background function sends an email in the background.

    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param body: EmailSchema: Get the email from the request body
    :return: A dictionary and not a response
    :doc-author: Trelent
    """
    message = MessageSchema(
        subject="Reset password of user",
        recipients=[body.email],
        template_body={"fullname": "Billy Jones", "position": "Bla-Bla"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="example_email.html")

    return {"message": "email has been sent"}


if __name__ == '__main__':
    uvicorn.run('send-email:app', port=8000, reload=True)
