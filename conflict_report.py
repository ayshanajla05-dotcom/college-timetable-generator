conflicts = []


def clear_conflicts():
    conflicts.clear()


def add_conflict(conflict_type, section, subject, message):

    conflicts.append({
        "type": conflict_type,
        "section": section,
        "subject": subject,
        "message": message
    })


def get_conflicts():
    return conflicts