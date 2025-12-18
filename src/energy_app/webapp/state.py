import uuid


def get_demo_user_id(session_state) -> str:
    if "user_id" not in session_state:
        session_state["user_id"] = f"demo-{uuid.uuid4()}"
    return session_state["user_id"]
