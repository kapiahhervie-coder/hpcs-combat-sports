def user_has_access(user):
    ALLOWED_GROUPS = {"cabor_1", "cabor_2", "cabor_3", "cabor_4", "pjok"}
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()
