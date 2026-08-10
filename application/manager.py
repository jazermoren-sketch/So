from application.storage import (
    load_stages,
    save_stages,
)


class StageManager:

    @staticmethod
    def create_stage(name: str):

        stages = load_stages()

        if name in stages:
            return False

        stages[name] = {
            "questions": []
        }

        save_stages(stages)

        return True

    @staticmethod
    def delete_stage(name: str):

        stages = load_stages()

        if name not in stages:
            return False

        del stages[name]

        save_stages(stages)

        return True

    @staticmethod
    def list_stages():

        return load_stages()

    @staticmethod
    def add_question(stage, question):

        stages = load_stages()

        if stage not in stages:
            return False

        stages[stage]["questions"].append(question)

        save_stages(stages)

        return True

    @staticmethod
    def edit_question(stage, index, question):

        stages = load_stages()

        if stage not in stages:
            return False

        questions = stages[stage]["questions"]

        if index < 0 or index >= len(questions):
            return False

        questions[index] = question

        save_stages(stages)

        return True

    @staticmethod
    def remove_question(stage, index):

        stages = load_stages()

        if stage not in stages:
            return False

        questions = stages[stage]["questions"]

        if index < 0 or index >= len(questions):
            return False

        questions.pop(index)

        save_stages(stages)

        return True

    @staticmethod
    def get_questions(stage):

        stages = load_stages()

        if stage not in stages:
            return []

        return stages[stage]["questions"]

    @staticmethod
    def stage_exists(stage):

        stages = load_stages()

        return stage in stages