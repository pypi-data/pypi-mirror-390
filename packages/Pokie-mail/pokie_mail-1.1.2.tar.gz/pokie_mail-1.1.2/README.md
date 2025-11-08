# Welcome to Pokie-mail

[![Tests](https://github.com/oddbit-project/pokie-mail/workflows/Tests/badge.svg)](https://github.com/oddbit-project/pokie-mail/actions)
[![pypi](https://img.shields.io/pypi/v/pokie-mail.svg)](https://pypi.org/project/pokie-mail/)
[![license](https://img.shields.io/pypi/l/pokie-mail.svg)](https://git.oddbit.org/OddBit/pokie-mail/src/branch/master/LICENSE)


Transactional SMTP email support for Pokie applications

# Features

The pokie-mail package implements a simple templating system for emails, as well as a job queue to send them. The templating
system supports placeholders and locales, and has the notion of channel - allowing it to be extended to use other mechanisms
such as push notifications or other rich notification providers.

The provided worker will attempt to send upto 10k emails per batch from the queue, using the configured [rick_mailer](https://github.com/oddbit-project/rick-mailer) 
sink for channel 0 submissions.

Other channel submissions (such as site notifications and push notifications) need to be implemented with their specific
behaviour.

# Usage

## How to add templates

The module supports both embedded html templates and text templates, as well as a list of placeholders and default values.
Application templates can either be imported directly via SQL or using Pokie's fixture mechanism. There are also functions
that enable adding new templates at runtime.

Templates can have placeholders and default values; Template placeholders are freeform - one can use whatever format is suitable
to represent the placeholders, but a common form is to use double placeholders, such as *{{placeholder_name}}*:

```python

    template = MessageTemplateRecord(
        template="template_name",
        language="en",
        channel=0,
        label="this is an example template",
        subject="template subject",
        body="the quick {{color}} {{animal}} {{what}} over the lazy dog", # text version
        html="<b>the quick {{color}} {{animal}} {{what}} over the lazy dog</b>", # html version
        placeholders={
            "{{color}}": "blue", # placeholder and default value
            "{{animal}}": "duck", 
            "{{what}}": "flies"
        },
    )

```

## Integrate with your application

Just add "pokie_mail" module to the module list, add *MailConfigTemplate* to your configuration and optionally override
the default SMTP parameters if necessary:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie_mail.config import MailConfigTemplate


# your application configuration

class Config(EnvironmentConfig, PokieConfig, MailConfigTemplate):
    # ==== Other configuration settings =====
    (...)
    
    # ==== MailConfigTemplate settings =====
    # number of emails to send at once
    MAILS_PER_RUN = 10000
    
    # SMTP Configuration [to use with mailhog]
    SMTP_HOST = "localhost"
    SMTP_PORT = 1025
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""

    
def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = [
        'pokie_mail', # enable pokie email
        # your other modules below
        (...)
        
    ]

    # factories to run
    factories = [PgSqlFactory]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == '__main__':
    main.cli()
```

## Assembling messages


Queuing a message is a two-step process - first get the message builder for the desired template, then the resulting message
is queued using the MessageQueueService:

```python
from pokie_mail.service import MessageTemplateService
from pokie_mail.service import MessageQueueService
from rick.mixin import Injectable
from pokie.constants import DI_SERVICES
from pokie_mail.constants import SVC_MESSAGE_TEMPLATE, SVC_MESSAGE_QUEUE

class SomeService(Injectable):

    def notify_user(self, email:str, first_name:str, last_name:str):
        
        # get template service
        svc_template = self.get_di().get(DI_SERVICES).get(SVC_MESSAGE_TEMPLATE) # type: MessageTemplateService

        # get queue service
        svc_queue = self.get_di().get(DI_SERVICES).get(SVC_MESSAGE_QUEUE) # type: MessageQueueService

        # get template builder for the template "template_notify_user" to assemble the message
        builder = svc_template.get_builder("template_notify_user", "en")
        
        # now assemble the message record
        message = builder.assemble(
            msg_from="nobody@somewhere.local",
            msg_to=email,
            data= {
                "{{first_name}}": first_name,
                "{{last_name}}": last_name,                
            }
        )
        
        # queue message for sending
        message_id = svc_queue.queue(message)
```

# Configuration

SMTP configuration is performed in the main config class, and can be overridden by using the traditional environment
variable mechanisms and/or StrOrFile for credential loading:
```python
from rick.resource.config import EnvironmentConfig
from pokie.config.template import BaseConfigTemplate, PgConfigTemplate, TestConfigTemplate
from pokie_mail.config import MailConfigTemplate

# base configuration
class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate, TestConfigTemplate, MailConfigTemplate):
    # ==== Other configuration settings =====
    (...)
    
    # ==== MailConfigTemplate settings =====
    # number of emails to send at once
    MAILS_PER_RUN = 10000
    
    # SMTP Configuration [to use with mailhog]
    SMTP_HOST = "localhost"
    SMTP_PORT = 1025
    SMTP_USE_TLS = False
    SMTP_USE_SSL = False
    SMTP_DEBUG = False
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""
    SMTP_DEFAULT_SENDER = None
    SMTP_TIMEOUT = None
    SMTP_SSL_KEYFILE = None
    SMTP_SSL_CERTFILE = None
```
The above example can be used to forward email to [MailHog](https://github.com/mailhog/MailHog) during development.

## Sending email in development mode

Use the configuration shown previously to use [MailHog](https://github.com/mailhog/MailHog) to intercept mail messages.
To run the mail queue, open the job runner in a separate console:

```shell
$ python3 main.py job:run
```

## Sending email in production

To send email in production, configure a background process to run the job runner:

```shell
$ python3 main.py job:run
```



# Running tests

Running tests require a PostgreSQL database server with access credentials that can run CREATE DATABASE/DROP DATABASE 
commands. The test database is created automatically.

## running with pytest

Install required dependencies:

```shell
$ pip3 install -r requirements-dev.txt
```

Define the appropriate environment variables to access the database, and run pytest (optionally with code coverage):
```shell
$ TEST_DB_HOST='localhost' TEST_DB_USER='db_user' TEST_DB_PASSWORD='db_password' python3 main.py pytest [-cov=pokie_mail]
```

## running with tox

Edit tox.ini and set the appropriate database credentials, then just run tox with the desired environment, eg:  

```shell
$ tox -e py310
```

