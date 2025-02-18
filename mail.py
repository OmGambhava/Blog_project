from fastapi_mail import FastMail, ConnectionConfig


class Config:
    MAIL_USERNAME = "dummy01064444@gmail.com"
    MAIL_PASSWORD = "lglmwwxhvxmjncqc"
    MAIL_FROM = "dummy01064444@gmail.com"
    MAIL_PORT = 587
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False

conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_STARTTLS=Config.MAIL_STARTTLS,
    MAIL_SSL_TLS=Config.MAIL_SSL_TLS,
)

fm = FastMail(conf)