from .interface import track


def handler(event, context):
    try:
        is_success = track.post_current_playing()
        if not is_success:
            return {"status": "ERROR", "message": "Failed to post current playing."}
        return {"status": "SUCCESS"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


if __name__ == "__main__":
    # python -m notificate_current_playing
    print(handler({}, {}))
