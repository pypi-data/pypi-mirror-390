import pytest

from pokie_mail.constants import SVC_MESSAGE_TEMPLATE, SVC_MESSAGE_QUEUE
from pokie_mail.dto import MessageTemplateRecord
from pokie_mail.service import MessageTemplateService, MessageQueueService
from tests.unit.constants import TPL_1_NAME, TPL_LOCALE, TPL_2_NAME


@pytest.fixture
def svc_template(pokie_service_manager) -> MessageTemplateService:
    return pokie_service_manager.get(SVC_MESSAGE_TEMPLATE)


@pytest.fixture
def svc_queue(pokie_service_manager) -> MessageQueueService:
    return pokie_service_manager.get(SVC_MESSAGE_QUEUE)


@pytest.fixture
def template_1() -> MessageTemplateRecord:
    return MessageTemplateRecord(
        template=TPL_1_NAME,
        language=TPL_LOCALE,
        channel=0,
        label="label for template 1",
        subject="template subject",
        body="",
        html="",
        placeholders="",
    )


@pytest.fixture
def template_2() -> MessageTemplateRecord:
    return MessageTemplateRecord(
        template=TPL_2_NAME,
        language=TPL_LOCALE,
        channel=0,
        label="label for base_system_template",
        subject="template subject",
        body="the quick {{color}} {{animal}} {{what}} over the lazy dog",
        html="the quick {{color}} {{animal}} {{what}} over the lazy dog",
        placeholders={"{{color}}": "blue", "{{animal}}": "duck", "{{what}}": "flies"},
    )
