from enum import Enum, auto


class IncreasingEnum(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        # if len(last_values) == 0:
        #     return 0
        # return last_values[-1] + 1
        if name == "INTERNET":
            return -1
        if name == "OTHER_PERMISSIONS":
            return 0.05
        return count / 5


class Permissions(IncreasingEnum):
    VIBRATE = auto()
    SYSTEM_ALERT_WINDOW = auto()
    ACCESS_NETWORK_STATE = auto()
    ACCESS_WIFI_STATE = auto()
    WAKE_LOCK = auto()
    RECEIVE = auto()
    READ_APP_BADGE = auto()
    PROVIDER_INSERT_BADGE = auto()
    FOREGROUND_SERVICE = auto()
    BROADCAST_BADGE = auto()
    CHANGE_BADGE = auto()
    UPDATE_BADGE = auto()
    MANAGE_ACCOUNTS = auto()
    BIND_GET_INSTALL_REFERRER_SERVICE = auto()
    C2D_MESSAGE = auto()
    USE_CREDENTIALS = auto()
    WRITE_SETTINGS = auto()
    USE_FINGERPRINT = auto()
    MODIFY_AUDIO_SETTINGS = auto()

    WRITE = auto()
    READ = auto()
    READ_GSERVICES = auto()
    BLUETOOTH = auto()
    UPDATE_COUNT = auto()
    BLUETOOTH_ADMIN = auto()
    READ_SETTINGS = auto()
    CHANGE_WIFI_STATE = auto()
    RECORD_AUDIO = auto()
    CAMERA = auto()
    GET_ACCOUNTS = auto()
    READ_CONTACTS = auto()
    UPDATE_SHORTCUT = auto()
    INSTALL_SHORTCUT = auto()
    BILLING = auto()
    RECEIVE_BOOT_COMPLETED = auto()
    GET_TASKS = auto()
    READ_PHONE_STATE = auto()
    WRITE_EXTERNAL_STORAGE = auto()
    ACCESS_COARSE_LOCATION = auto()
    READ_EXTERNAL_STORAGE = auto()
    ACCESS_FINE_LOCATION = auto()

    INTERNET = auto()
    OTHER_PERMISSIONS = auto()

cats_old = {
    "games": 1.6,
    "learning": 1.4,
    "social media": 1.6,
    "sports": 1.1,
    "multimedia": 1.4,
    "health": 1.8,
    "office": 1.2,
    "customization": 1.6,
    "shopping": 1.6,
}

cats_new = {
    "x0_Casual": 1.6,
    "x0_Comics": 1.6,
    "x0_Arcade & Action": 1.6,
    "x0_Books & Reference": 1.6,
    "x0_Brain & Puzzle": 1.6,
    "x0_Lifestyle": 1.6,
    "x0_Media & Video": 1.6,
    "x0_Music & Audio": 1.6,
    "x0_News & Magazines": 1.6,
    "x0_Photography": 1.6,
    "x0_Productivity": 1.6,
    "x0_Racing": 1.6,
    "x0_Sports": 1.6,
    "x0_Sports Games": 1.6,
    "x0_Weather": 1.6,

    "x0_Communication": 1.3,
    "x0_Business": 1.3,
    "x0_Education": 1.3,
    "x0_Entertainment": 1.3,
    "x0_Health & Fitness": 1.3,
    "x0_Personalization": 1.3,
    "x0_Social": 1.3,
    "x0_Tools": 1.3,
    "x0_Transportation": 1.3,
    "x0_Travel & Local": 1.3,

    "x0_Cards & Casino": 1,
    "x0_Finance": 1,
    "x0_Libraries & Demo": 1,
    "x0_Medical": 1,
    "x0_Shopping": 1,
}

def heuristic(row):
    """
    0: normal
    1: anomaly

    :param row:
    :return:
    """
    keys = [k for k in row.keys() if k in Permissions.__members__.keys()]
    cats = [k for k in row.keys() if k not in Permissions.__members__.keys()][1:]

    return int(
        sum([Permissions[k].value * row[k] for k in keys]) + 
        sum([cats_old.get(k, 1.0) * row[k] for k in cats]) 
    > 110)


new_perm_cats_map = {
    "default": 1,
    "development tools": 1,
    "hardware controls": 2,
    "network communication": 2,
    "phone calls": 3,
    "services that cost you money": 3,
    "storage": 2,
    "system tools": 3,
    "your accounts": 4,
    "your messages": 4,
    "your location": 4,
    "your personal information": 5,
}

def heuristic_priv_new(row):
    """
    0: normal
    1: anomaly

    :param row: the table row
    :return:
    """
    
    perms = [k for k in row.keys() if k.endswith(')')]
    cats = [k for k in row.keys() if k.startswith('x0_')]

    perm_score = sum([
        new_perm_cats_map[k.split(' : ')[0]] * 
        ((k[-2] == 'd') + 1) * 
        row[k] 
        for k in perms
    ])
    purpose_score = sum([
        cats_new[k] *
        row[k] 
        for k in cats
    ])

    return int(perm_score*purpose_score > 150)

# print(list(Permissions)[:3])
# print(Permissions.__members__.keys())
