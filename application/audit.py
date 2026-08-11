import time
from application.storage import load_applications, save_application


def _app(guild_id, user_id):
    apps = load_applications(guild_id)
    return apps.get(str(user_id), {}), apps


def log(guild_id, user_id, action, actor_id=None, details=None):
    app, apps = _app(guild_id, user_id)
    history = list(app.get("history", []))
    history.append({"action": action, "actor_id": actor_id, "details": details or {}, "at": time.time()})
    app["history"] = history[-100:]
    apps[str(user_id)] = app
    save_applications(guild_id, apps)


def add_note(guild_id, user_id, actor_id, note):
    app, apps = _app(guild_id, user_id)
    notes = list(app.get("internal_notes", []))
    notes.append({"actor_id": actor_id, "note": note, "at": time.time()})
    app["internal_notes"] = notes[-100:]
    apps[str(user_id)] = app
    save_applications(guild_id, apps)


def assign(guild_id, user_id, reviewer_id):
    app, apps = _app(guild_id, user_id)
    app["assigned_reviewer"] = reviewer_id
    app["locked_by"] = reviewer_id
    app["locked_at"] = time.time()
    apps[str(user_id)] = app
    save_applications(guild_id, apps)
    log(guild_id, user_id, "assigned", reviewer_id, {"reviewer_id": reviewer_id})


def unlock(guild_id, user_id, actor_id=None):
    app, apps = _app(guild_id, user_id)
    app.pop("locked_by", None)
    app.pop("locked_at", None)
    apps[str(user_id)] = app
    save_applications(guild_id, apps)
    log(guild_id, user_id, "unlocked", actor_id)


def history(guild_id, user_id):
    return list(load_applications(guild_id).get(str(user_id), {}).get("history", []))
