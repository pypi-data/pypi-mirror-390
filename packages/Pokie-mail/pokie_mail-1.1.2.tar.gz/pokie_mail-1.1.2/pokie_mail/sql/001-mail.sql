CREATE EXTENSION pgcrypto;

CREATE TABLE message_template(
    id_message_template SERIAL NOT NULL PRIMARY KEY,
    template VARCHAR(128) NOT NULL,
    "language" VARCHAR(8) NOT NULL,
    channel INT NOT NULL DEFAULT 0,
    created timestamp with time zone default Now(),
    label TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT DEFAULT '',
    html TEXT DEFAULT '',
    placeholders TEXT DEFAULT ''
);

CREATE TABLE message_queue(
    id_message_queue uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created timestamp with time zone default Now(),
    channel INT NOT NULL DEFAULT 0,
    status CHAR(1) DEFAULT 'Q', -- Q: queued, S: sent
    sent timestamp with time zone default NULL,
    msg_from TEXT,
    msg_to TEXT,
    title TEXT,
    content TEXT DEFAULT '',
    html TEXT DEFAULT NULL
);

CREATE INDEX mail_queue_idx01 on message_queue(created, channel, status);
