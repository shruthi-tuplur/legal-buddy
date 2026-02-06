# memory_store.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional
import time
import uuid

Role = Literal["system", "user", "assistant"]

@dataclass
class Message:
    role: Role
    content: str
    ts: float = field(default_factory=lambda: time.time())

@dataclass
class Session:
    session_id: str
    case_id: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_ts: float = field(default_factory=lambda: time.time())
    updated_ts: float = field(default_factory=lambda: time.time())

class InMemorySessionStore:
    def __init__(self, max_sessions: int = 500):
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = max_sessions

    def _evict_if_needed(self):
        if len(self.sessions) <= self.max_sessions:
            return
        oldest = sorted(self.sessions.values(), key=lambda s: s.updated_ts)[0]
        self.sessions.pop(oldest.session_id, None)

    def get_or_create(self, session_id: Optional[str]) -> Session:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        new_id = session_id or str(uuid.uuid4())
        sess = Session(session_id=new_id)
        self.sessions[new_id] = sess
        self._evict_if_needed()
        return sess

    def append(self, session: Session, role: Role, content: str):
        session.messages.append(Message(role=role, content=content))
        session.updated_ts = time.time()
