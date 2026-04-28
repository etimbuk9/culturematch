def calculate_match_score(student, job):

    def skill_score(student_skills, required):
        if not required:
            return 0

        levels = {
            "Beginner": 0.4,
            "Intermediate": 0.7,
            "Advanced": 0.9,
            "Expert": 1.0
        }

        total = sum(
            levels.get(student_skills.get(s, "Beginner"), 0.3)
            for s in required
        )

        return total / len(required)

    def overlap(a, b):
        if not b:
            return 0
        return len(set(a) & set(b)) / len(b)

    return round(100 * (
        0.5 * skill_score(student["skills"], job["skills"]) +
        0.2 * overlap(student["culture"], job["culture"]) +
        0.15 * overlap(student["personality"], job["personality"]) +
        0.15 * overlap(student["character"], job["character"])
    ), 1)
