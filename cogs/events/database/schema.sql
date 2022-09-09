CREATE TABLE IF NOT EXISTS Event (
  Id        INTEGER NOT NULL,
  MessageId INTEGER NOT NULL,
  PRIMARY KEY (Id)
);

CREATE TABLE IF NOT EXISTS Guest (
  Name    TEXT    NOT NULL,
  EventId INTEGER NOT NULL,
  PRIMARY KEY (Name, EventId),
  UNIQUE (Name COLLATE NOCASE),
  FOREIGN KEY (EventId) REFERENCES Event (Id)
);
