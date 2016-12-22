from musicleague.models import MessengerContext


STATUS_DEFAULT = 0
STATUS_LINK_ACCOUNT = 1


def create_context(messenger_id, status=STATUS_DEFAULT, user=None):
    context = MessengerContext(id=messenger_id, user=user)
    context.save()
    return context


def update_context_status(messenger_id, status, context=None):
    if context is None:
        context = get_context(messenger_id)
        if context is None:
            return

    context.status = status
    context.save()
    return context


def get_context(messenger_id):
    try:
        return MessengerContext.objects(id=messenger_id).get()
    except MessengerContext.DoesNotExist:
        return None
