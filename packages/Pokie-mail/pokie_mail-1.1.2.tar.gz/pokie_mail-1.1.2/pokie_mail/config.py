from rick.resource.config import StrOrFile


# pokie_mail SMTP configuration
class MailConfigTemplate:
    # number of emails to send at once
    MAILS_PER_RUN = 10000

    # Message channel configuration
    channels = {"0": "SMTP"}
    SMTP_HOST = "localhost"
    SMTP_PORT = 25
    SMTP_USE_TLS = False
    SMTP_USE_SSL = False
    SMTP_DEBUG = False
    SMTP_USERNAME = StrOrFile("username")
    SMTP_PASSWORD = StrOrFile("password")
    SMTP_DEFAULT_SENDER = None
    SMTP_TIMEOUT = None
    SMTP_SSL_KEYFILE = None
    SMTP_SSL_CERTFILE = None
