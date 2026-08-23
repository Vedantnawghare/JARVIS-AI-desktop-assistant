from app.memory.store import MemoryStore


memory = MemoryStore()


def remember(key: str, value: str) -> str:
    return memory.remember(
        key,
        value,
    )


def recall(key: str) -> str:
    return memory.recall(key)


def forget(key: str) -> str:
    return memory.forget(key)