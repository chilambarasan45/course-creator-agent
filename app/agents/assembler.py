def assemble_course(topic: str, level: str, modules_data: list[dict]) -> dict:
    """
    Combines curriculum, content, and quizzes into one final course object.

    Args:
        topic: the course topic
        level: difficulty level
        modules_data: list of dicts, each containing title, content, quiz

    Returns:
        final structured course dictionary
    """
    course = {
        "topic": topic,
        "level": level,
        "modules": modules_data
    }
    return course