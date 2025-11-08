from typing import List, Optional

from pokie.constants import DI_DB

from pokie_mail.constants import STATUS_QUEUED, VALID_STATUS
from pokie_mail.dto import MessageQueueRecord
from pokie_mail.repository import MessageQueueRepository
from rick.mixin import Injectable


class MessageQueueService(Injectable):
    def queue(self, record: MessageQueueRecord) -> str:
        record.status = STATUS_QUEUED
        return self.repo_queue.insert_pk(record)

    def list_by_status(
        self, channel: int, status: str, limit: int = 1000
    ) -> List[MessageQueueRecord]:
        return self.repo_queue.find_by_status(channel, status, limit)

    def valid_status(self, status: str) -> bool:
        return status in VALID_STATUS

    def update_status(self, id_record: str, status: str, raise_on_error=True):
        if not self.valid_status(status):
            if raise_on_error:
                raise RuntimeError(
                    "MessageQueueService.update_status(): invalid status '{}'".format(
                        status
                    )
                )
            return
        self.repo_queue.update_status(id_record, status)

    def fetch_for_processing(self, channel: int) -> Optional[MessageQueueRecord]:
        """
        Pick & lock a message for processing
        :return: MessageQueueRecord or None
        """
        return self.repo_queue.find_first_and_lock(channel, STATUS_QUEUED)

    def purge(self):
        """
        Removes all queued records
        :return:
        """
        return self.repo_queue.truncate()

    @property
    def repo_queue(self) -> MessageQueueRepository:
        return MessageQueueRepository(self.get_di().get(DI_DB))
