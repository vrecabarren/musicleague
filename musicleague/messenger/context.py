from musicleague.persistence.models import MessengerContext


STATUS_DEFAULT = 0
STATUS_LINK_ACCOUNT = 1


def create_context(messenger_id, status=STATUS_DEFAULT, user=None):
    context = MessengerContext(id=messenger_id, status=status, user=user)
    # TODO Persist
    return context


def update_context_status(messenger_id, status, context=None):
    if context is None:
        context = get_context(messenger_id)
        if context is None:
            return

    context.status = status
    # TODO Persist
    return context


def get_context(messenger_id):
    # TODO Persist
    return None
