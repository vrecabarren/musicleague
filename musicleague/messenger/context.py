from musicleague.models import MessengerContext


def create_context(messenger_id, user=None):
    context = MessengerContext(id=messenger_id, user=user)
    context.save()
    return context


def get_context(messenger_id):
    try:
        return MessengerContext.objects(id=messenger_id).get()
    except MessengerContext.DoesNotExist:
        return None
