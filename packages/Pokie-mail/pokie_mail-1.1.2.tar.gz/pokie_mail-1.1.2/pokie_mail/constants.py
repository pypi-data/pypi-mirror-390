# Version
POKIE_MAIL_VERSION = ["1", "1", "2"]


def get_version():
    return ".".join(POKIE_MAIL_VERSION)


# Service names

SVC_MESSAGE_QUEUE = "sv_pokie_mail_msg_queue"
SVC_MESSAGE_TEMPLATE = "sv_pokie_mail_msg_template"

# MessageQueueRecord status
STATUS_DRAFT = "D"  # not committed to database yet
STATUS_QUEUED = "Q"
STATUS_LOCKED = "L"
STATUS_FAILED = "F"
STATUS_SENT = "S"

VALID_STATUS = [
    STATUS_QUEUED,
    STATUS_LOCKED,
    STATUS_FAILED,
    STATUS_SENT,
]

# communication channels

CHANNEL_SMTP = 0

# SMTP Configuration variables
CFG_SMTP_HOST = "smtp_host"
CFG_SMTP_PORT = "smtp_port"
CFG_SMTP_USE_TLS = "smtp_use_tls"
CFG_SMTP_USE_SSL = "smtp_use_ssl"
CFG_SMTP_DEBUG = "smtp_debug"
CFG_SMTP_USERNAME = "smtp_username"
CFG_SMTP_PASSWORD = "smtp_password"
CFG_SMTP_DEFAULT_SENDER = "smtp_default_sender"
CFG_SMTP_TIMEOUT = "smtp_timeout"
CFG_SMTP_SSL_KEYFILE = "smtp_ssl_keyfile"
CFG_SMTP_SSL_CERTFILE = "smtp_ssl_certfile"
