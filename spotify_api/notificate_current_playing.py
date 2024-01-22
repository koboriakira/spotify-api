from interface import track


def handler(event, context):
    return track.post_current_playing()


if __name__ == "__main__":
    # python -m notificate_current_playing
    print(handler({}, {}))
