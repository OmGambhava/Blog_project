from fastapi_mail import FastMail, ConnectionConfig
import os
from dotenv import load_dotenv
load_dotenv()

mail_id = os.getenv("MAIL_ID")
mail_password = os.getenv("MAIL_PASSWORD")
mail_port = os.getenv("MAIL_PORT")
mail_server = os.getenv("MAIL_SERVER")

class Config:
    MAIL_USERNAME = mail_id
    MAIL_PASSWORD = mail_password
    MAIL_FROM = mail_id
    MAIL_PORT = mail_port
    MAIL_SERVER = mail_server
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False

conf = ConnectionConfig(
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_STARTTLS = Config.MAIL_STARTTLS,
    MAIL_SSL_TLS = Config.MAIL_SSL_TLS,
)

fm = FastMail(conf)