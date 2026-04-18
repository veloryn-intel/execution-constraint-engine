def append_log(record):
    import json

    try:
        with open("veloryn_logs.jsonl", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
    except Exception:
        pass


def export_logs(path):
    import os
    import shutil

    try:
        if os.path.exists("veloryn_logs.jsonl"):
            shutil.copy("veloryn_logs.jsonl", path)
    except Exception:
        pass
