from application.storage import load_stages, save_stages


class StageManager:
    @staticmethod
    def create_stage(guild_id, name: str):
        stages = load_stages(guild_id)
        if name in stages: return False
        stages[name] = {"questions": []}; save_stages(guild_id, stages); return True

    @staticmethod
    def delete_stage(guild_id, name: str):
        stages = load_stages(guild_id)
        if name not in stages: return False
        del stages[name]; save_stages(guild_id, stages); return True

    @staticmethod
    def list_stages(guild_id): return load_stages(guild_id)

    @staticmethod
    def add_question(guild_id, stage, question):
        stages = load_stages(guild_id)
        if stage not in stages: return False
        stages[stage]["questions"].append(question); save_stages(guild_id, stages); return True

    @staticmethod
    def edit_question(guild_id, stage, index, question):
        stages = load_stages(guild_id)
        if stage not in stages: return False
        questions = stages[stage]["questions"]
        if index < 0 or index >= len(questions): return False
        questions[index] = question; save_stages(guild_id, stages); return True

    @staticmethod
    def remove_question(guild_id, stage, index):
        stages = load_stages(guild_id)
        if stage not in stages: return False
        questions = stages[stage]["questions"]
        if index < 0 or index >= len(questions): return False
        questions.pop(index); save_stages(guild_id, stages); return True

    @staticmethod
    def get_questions(guild_id, stage):
        stages = load_stages(guild_id)
        return stages[stage]["questions"] if stage in stages else []

    @staticmethod
    def stage_exists(guild_id, stage): return stage in load_stages(guild_id)
