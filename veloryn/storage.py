TASK_STORAGE: dict[str, dict] = {}


def get_task(task_id):
    return TASK_STORAGE.get(task_id)


def save_task(task_id, state):
    TASK_STORAGE[task_id] = state
    return state
