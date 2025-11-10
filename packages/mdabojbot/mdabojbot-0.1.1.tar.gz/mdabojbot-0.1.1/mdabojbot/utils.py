from decouple import config  # type: ignore


def get_token() -> str:
    token: str = config("TELEGRAM_TOKEN")
    if token is None:
        raise ValueError("Can not get a telegram token.")
    return token


def get_path_to_db() -> str:
    path_to_db: str = config("FULL_PATH_TO_DB")
    if path_to_db is None:
        raise ValueError("Can not get a path to DB.")
    return path_to_db


def get_superuser_telegram_id() -> str:
    superuser_telegram_id: str = config("SUPERUSER_TELEGRAM_ID")
    if superuser_telegram_id is None:
        raise ValueError("Can not get a superuser Telegram ID.")
    return superuser_telegram_id
