from typing import List, Optional

from rick_db import Repository
from rick_db.sql import Update
from pokie_mail.dto import MessageQueueRecord, MessageTemplateRecord
from rick.util.datetime import iso8601_now


class MessageQueueRepository(Repository):
    def __init__(self, db):
        super().__init__(db, MessageQueueRecord)

    def find_by_status(self, channel, status, limit=1000) -> List[MessageQueueRecord]:
        sql, values = (
            self.select()
            .where(MessageQueueRecord.status, "=", status)
            .where(MessageQueueRecord.channel, "=", channel)
            .limit(limit)
            .assemble()
        )

        with self.cursor() as c:
            return c.fetchall(sql, values, self._record)

    def update_status(self, id_record: str, status: str):
        record = self.fetch_pk(id_record)
        if record is not None:
            record.status = status
            if status == "S":
                record.sent = iso8601_now()
            self.update(record)

    def find_first_and_lock(
        self, channel: int, status: str = "Q"
    ) -> Optional[MessageQueueRecord]:
        """
        Locks a queued message and returns the record
        :param channel:
        :param status: previous status of record to be locked
        :return:
        """

        qry = (
            self.select(cols=[MessageQueueRecord.id])
            .where(MessageQueueRecord.status, "=", status)
            .where(MessageQueueRecord.channel, "=", channel)
            .limit(1)
            .for_update()
        )

        sql, values = (
            Update(self.dialect)
            .table(self.table_name, self.schema)
            .values({MessageQueueRecord.status: "L"})
            .where(MessageQueueRecord.id, "=", qry)
            .returning()
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchall(sql, values, self._record)
            if len(result) > 0:
                return result[0]
            return None

    def truncate(self):
        sql = "TRUNCATE TABLE {}".format(
            self.dialect.table(self.table_name, schema=self.schema)
        )
        with self.cursor() as c:
            c.exec(sql)


class MessageTemplateRepository(Repository):
    def __init__(self, db):
        super().__init__(db, MessageTemplateRecord)

    def find_template(
        self, template: str, language: str, channel: int
    ) -> Optional[MessageTemplateRecord]:
        sql, values = (
            self.select()
            .where(MessageTemplateRecord.template, "=", template)
            .where(MessageTemplateRecord.language, "=", language)
            .where(MessageTemplateRecord.channel, "=", channel)
            .limit(1)
            .assemble()
        )

        with self.cursor() as c:
            return c.fetchone(sql, values, self._record)
