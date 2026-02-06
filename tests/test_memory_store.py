from memory_store import InMemorySessionStore, Session


def test_get_or_create_creates_session():
    store = InMemorySessionStore()

    sess = store.get_or_create("abc")

    assert isinstance(sess, Session)
    assert sess.session_id == "abc"
    assert sess.messages == []


def test_get_or_create_returns_existing_session():
    store = InMemorySessionStore()

    sess1 = store.get_or_create("abc")
    sess2 = store.get_or_create("abc")

    assert sess1 is sess2


def test_append_adds_message():
    store = InMemorySessionStore()
    sess = store.get_or_create("abc")

    store.append(sess, role="user", content="Hello")

    assert len(sess.messages) == 1
    assert sess.messages[0].role == "user"
    assert sess.messages[0].content == "Hello"
