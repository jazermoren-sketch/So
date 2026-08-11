import json
import os

DATA_FOLDER = "application"
STAGES_FILE = os.path.join(DATA_FOLDER, "stages.json")
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")
ANSWERS_FILE = os.path.join(DATA_FOLDER, "answers.json")
APPLICATIONS_FILE = os.path.join(DATA_FOLDER, "applications.json")
MIGRATION_GUILD_ID = "1510671861254717540"

def _defaults():
    return {
        "reviewer": None, "reviewers": [], "review_channel": None, "result_channel": None, "appeal_channel": None, "apply_channel": None,
        "accepted_role": None, "rejected_role": None, "applications_open": True, "test_questions": 10, "test_pass_percent": 70,
        "test_timer_minutes": 10, "test_attempts": 1, "random_questions": True, "application_logs": True, "application_dm_notifications": True,
        "prevent_duplicate": True, "allow_reapply": True, "application_status": True, "test_pass_fail": True, "test_timer": True,
        "test_attempts_enabled": True, "application_requirements": False, "scoring_enabled": False, "score_max": 10, "score_min": 5,
        "question_scoring": False, "reviewer_voting": False, "required_approvals": 1, "appeals_enabled": True, "appeal_cooldown_hours": 168,
        "appeal_limit": 1, "reapply_cooldown_hours": 72, "auto_close_hours": 48, "auto_roles_by_score": [],
        "review_lock": True, "assignment_required": False, "internal_notes": True, "audit_logs": True,
        "expiry_enabled": True, "review_expiry_hours": 48, "appeal_reopen_role": True
    }

def _load_json(path, default):
    if not os.path.exists(path): return default
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except (json.JSONDecodeError, OSError): return default

def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def _create_file(path, default_data):
    if not os.path.exists(path): _save_json(path, default_data)

def _guild_store(path, default):
    data = _load_json(path, default)
    if isinstance(data, dict) and isinstance(data.get("guilds"), dict): return data
    migrated = {"guilds": {MIGRATION_GUILD_ID: data if isinstance(data, dict) else {}}}
    _save_json(path, migrated); return migrated

def _guild_data(path, guild_id, default):
    if not guild_id: raise ValueError("guild_id is required")
    store = _guild_store(path, default); key = str(guild_id)
    if key not in store["guilds"]:
        store["guilds"][key] = json.loads(json.dumps(default)) if isinstance(default, dict) else default; _save_json(path, store)
    return store["guilds"][key]

def _save_guild_data(path, guild_id, data, default):
    store = _guild_store(path, default); store["guilds"][str(guild_id)] = data; _save_json(path, store)

def setup():
    for path, default in ((STAGES_FILE, {}), (CONFIG_FILE, _defaults()), (ANSWERS_FILE, {}), (APPLICATIONS_FILE, {})): _create_file(path, default); _guild_store(path, default)

def load_stages(guild_id): setup(); return _guild_data(STAGES_FILE, guild_id, {})
def save_stages(guild_id, data): setup(); _save_guild_data(STAGES_FILE, guild_id, data, {})
def load_config(guild_id):
    setup(); data = _guild_data(CONFIG_FILE, guild_id, _defaults()); changed = False
    for key, value in _defaults().items():
        if key not in data: data[key] = value; changed = True
    if changed: save_config(guild_id, data)
    return data
def save_config(guild_id, data): setup(); _save_guild_data(CONFIG_FILE, guild_id, data, _defaults())
def load_answers(guild_id): setup(); return _guild_data(ANSWERS_FILE, guild_id, {})
def save_answers(guild_id, data): setup(); _save_guild_data(ANSWERS_FILE, guild_id, data, {})
def load_applications(guild_id): setup(); return _guild_data(APPLICATIONS_FILE, guild_id, {})
def save_applications(guild_id, data): setup(); _save_guild_data(APPLICATIONS_FILE, guild_id, data, {})
def save_application(guild_id, user_id, data):
    apps=load_applications(guild_id); apps[str(user_id)]=data; save_applications(guild_id,apps)
def get_application(guild_id,user_id): return load_applications(guild_id).get(str(user_id))
def delete_application(guild_id,user_id):
    apps=load_applications(guild_id); apps.pop(str(user_id),None); save_applications(guild_id,apps)
