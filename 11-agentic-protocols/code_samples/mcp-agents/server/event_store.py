#!/usr/bin/env python3
"""
Event Store Implementation for MCP Session Resumption

This module provides an in-memory event store that enables MCP session resumption
by storing and replaying events after client reconnection.
"""

import json
import logging
import sqlite3
from typing import Optional

from mcp.server.streamable_http import (
    EventCallback,
    EventId,
    EventMessage,
    EventStore,
    StreamId,
)
from mcp.types import JSONRPCMessage

logger = logging.getLogger(__name__)


class SimpleEventStore(EventStore):
    """Simple in-memory event store for testing resumption functionality."""

    def __init__(self):
        self._events: list[tuple[StreamId, EventId, JSONRPCMessage]] = []
        self._event_id_counter = 0
        logger.info("SimpleEventStore initialized")

    async def store_event(self, stream_id: StreamId, message: JSONRPCMessage) -> EventId:
        """Store an event and return its ID."""
        self._event_id_counter += 1
        event_id = str(self._event_id_counter)
        self._events.append((stream_id, event_id, message))
        logger.info(f"Stored event {event_id} for stream {stream_id}")
        return event_id

    async def replay_events_after(
        self,
        last_event_id: EventId,
        send_callback: EventCallback,
    ) -> StreamId | None:
        """Replay events after the specified ID."""
        logger.info(f"Replaying events after {last_event_id}")
        
        # Find the index of the last event ID
        start_index = None
        for i, (_, event_id, _) in enumerate(self._events):
            if event_id == last_event_id:
                start_index = i + 1
                break

        if start_index is None:
            # If event ID not found, start from beginning
            start_index = 0
            logger.info("Event ID not found, starting from beginning")

        stream_id = None
        # Replay events
        replayed_count = 0
        for _, event_id, message in self._events[start_index:]:
            await send_callback(EventMessage(message, event_id))
            replayed_count += 1
            # Capture the stream ID from the first replayed event
            if stream_id is None and len(self._events) > start_index:
                stream_id = self._events[start_index][0]

        logger.info(f"Replayed {replayed_count} events, stream_id: {stream_id}")
        return stream_id

    def get_event_count(self) -> int:
        """Get the total number of stored events."""
        return len(self._events)

    def clear_events(self) -> None:
        """Clear all stored events."""
        self._events.clear()
        self._event_id_counter = 0
        logger.info("Event store cleared")


class PersistentEventStore(EventStore):
    """
    Event store that persists events to disk using SQLite.
    
    In production, you would want to use a more robust database system,
    but SQLite is sufficient for local persistence.
    """
    
    def __init__(self, storage_path: str = "events.db"):
        self.storage_path = storage_path
        self._init_db()
        logger.info(f"PersistentEventStore initialized with {storage_path}")

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    async def store_event(self, stream_id: StreamId, message: JSONRPCMessage) -> EventId:
        """Store an event and return its ID."""
        # Serialize message
        try:
            # Try Pydantic v2
            message_json = message.model_dump_json()
        except AttributeError:
            try:
                # Try Pydantic v1
                message_json = message.json()
            except AttributeError:
                # Fallback to json dump if it's a dict or compatible object
                if hasattr(message, 'dict'):
                    message_json = json.dumps(message.dict())
                else:
                    # If it's a dict or other json serializable object
                    message_json = json.dumps(message)

        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (stream_id, message) VALUES (?, ?)",
                (stream_id, message_json)
            )
            event_id = str(cursor.lastrowid)
            conn.commit()

        logger.info(f"Stored event {event_id} for stream {stream_id}")
        return event_id
    
    async def replay_events_after(
        self,
        last_event_id: EventId,
        send_callback: EventCallback,
    ) -> StreamId | None:
        """Replay events after the specified ID."""
        logger.info(f"Replaying events after {last_event_id}")

        try:
            last_id_int = int(last_event_id)
        except ValueError:
            # If last_event_id is not an integer (e.g. empty string or special token), start from 0
            last_id_int = 0

        stream_id = None
        replayed_count = 0

        with sqlite3.connect(self.storage_path) as conn:
            # Use row factory to access columns by name
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, stream_id, message FROM events WHERE id > ? ORDER BY id ASC",
                (last_id_int,)
            )

            rows = cursor.fetchall()

            for row in rows:
                event_id = str(row['id'])
                message_json = row['message']
                stored_stream_id = row['stream_id']

                # Deserialize message
                try:
                    # Try Pydantic v2
                    message_obj = JSONRPCMessage.model_validate_json(message_json)
                except AttributeError:
                    try:
                        # Try Pydantic v1
                        message_obj = JSONRPCMessage.parse_raw(message_json)
                    except AttributeError:
                        # Fallback
                        message_dict = json.loads(message_json)
                        # If JSONRPCMessage is a class that accepts a dict in constructor
                        try:
                            message_obj = JSONRPCMessage(**message_dict)
                        except TypeError:
                             # Or just return the dict if the type hint is loose
                             message_obj = message_dict

                await send_callback(EventMessage(message_obj, event_id))
                replayed_count += 1

                if stream_id is None:
                    stream_id = stored_stream_id

        logger.info(f"Replayed {replayed_count} events, stream_id: {stream_id}")
        return stream_id

    def get_event_count(self) -> int:
        """Get the total number of stored events."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]

    def clear_events(self) -> None:
        """Clear all stored events."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("DELETE FROM events")
            conn.commit()
        logger.info("Persistent event store cleared")
