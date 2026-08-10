import json
import os

DATA_FOLDER = "application"

STAGES_FILE = os.path.join(DATA_FOLDER, "stages.json")
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")
ANSWERS_FILE = os.path.join(DATA_FOLDER, "answers.json")

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
    _create_file(CONFIG_FILE, {
        "reviewer": None,
        "review_channel": None,
        "apply_channel": None,
        "accepted_role": None,
        "applications_open": True
    })
    _create_file(ANSWERS_FILE, {})
    _create_file(APPLICATIONS_FILE, {})
    
def load_stages():
    setup()

    with open(STAGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_stages(data):
    setup()

    with open(STAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_config():
    setup()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    setup()

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_answers():
    setup()

    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_answers(data):
    setup()

    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_applications():
    setup()

    with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
        
def save_applications(data):
    setup()

    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_application(user_id, data):
    applications = load_applications()

    applications[str(user_id)] = data

    save_applications(applications)


def get_application(user_id):
    applications = load_applications()

    return applications.get(str(user_id))


def delete_application(user_id):
    applications = load_applications()

    applications.pop(str(user_id), None)

    save_applications(applications)