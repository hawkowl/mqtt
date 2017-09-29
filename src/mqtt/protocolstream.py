
import attr

@attr.s
class Message(object):

    pass



def parse_next_message(data):
    """
    Parse the next message from this MQTT data stream.
    """



    return message, remaining_data

def parse(data):

    messages = []

    while True:
        message, data = parse_next_message(data)

        if message:
            messages.append(message)
        else:
            return messages, data
