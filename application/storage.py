import json
import os

DATA_FOLDER = "application"
STAGES_FILE = os.path.join(DATA_FOLDER, "stages.json")
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")
ANSWERS_FILE = os.path.join(DATA_FOLDER, "answers.json")
APPLICATIONS_FILE = os.path.join(DATA_FOLDER, "applications.json")


def _create_file(path, default_data):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)


def setup():
    _create_file(STAGES_FILE, {})
    _create_file(CONFIG_FILE, _defaults())
    _create_file(ANSWERS_FILE, {})
    _create_file(APPLICATIONS_FILE, {})


def _defaults():
    return {
        "reviewer": None, "reviewers": [], "review_channel": None, "apply_channel": None,
        "accepted_role": None, "rejected_role": None, "applications_open": True,
        "test_questions": 10, "test_pass_percent": 70, "test_timer_minutes": 10,
        "test_attempts": 1, "random_questions": True, "application_logs": True,
        "application_dm_notifications": True, "prevent_duplicate": True, "allow_reapply": True,
        "application_status": True, "test_pass_fail": True, "test_timer": True, "test_attempts_enabled": True,
        "application_requirements": False
    }


def load_stages():
    setup(); return _load_json(STAGES_FILE, {})
def save_stages(data):
    setup(); _save_json(STAGES_FILE, data)
def load_config():
    setup(); data = _load_json(CONFIG_FILE, {}); changed = False
    for key, value in _defaults().items():
        if key not in data: data[key] = value; changed = True
    if changed: save_config(data)
    return data
def save_config(data):
    setup(); _save_json(CONFIG_FILE, data)
def load_answers():
    setup(); return _load_json(ANSWERS_FILE, {})
def save_answers(data):
    setup(); _save_json(ANSWERS_FILE, data)
def load_applications():
    setup(); return _load_json(APPLICATIONS_FILE, {})
def save_applications(data):
    setup(); _save_json(APPLICATIONS_FILE, data)
def save_application(user_id, data):
    applications = load_applications(); applications[str(user_id)] = data; save_applications(applications)
def get_application(user_id): return load_applications().get(str(user_id))
def delete_application(user_id):
    applications = load_applications(); applications.pop(str(user_id), None); save_applications(applications)
def _load_json(path, default):
    if not os.path.exists(path): return default
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except (json.JSONDecodeError, OSError): return default
def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)
