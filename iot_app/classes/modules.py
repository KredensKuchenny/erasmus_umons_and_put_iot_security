import datetime
from classes.api_endpoints import get_account_info


def is_logged(login_time, bearer_token):
    if login_time is not None and bearer_token is not None:
        login_time = datetime.datetime.fromisoformat(login_time)
        if datetime.datetime.now() > login_time:
            return 0
        else:
            account_info = get_account_info(bearer_token)
            if account_info["status_code"] == 200:
                return 1
            else:
                return 0
    else:
        return 0
