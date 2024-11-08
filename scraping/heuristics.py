from enum import Enum, auto
import Levenshtein


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
    MANAGE_ANIMATION_SPEED = auto()
    SYSTEM_ALERT_WINDOW = auto()
    EXPAND_STATUS_BAR = auto()
    # CONTROL_FLASHLIGHT = auto()
    CLOSE_BG_APPS = auto()
    ACCESS_NETWORK_STATE = auto()
    ACCESS_WIFI_STATE = auto()
    WAKE_LOCK = auto()
    RECEIVE = auto()
    WRITE_DISCTIONARY = auto()
    READ_APP_BADGE = auto()
    PROVIDER_INSERT_BADGE = auto()
    FOREGROUND_SERVICE = auto()
    SET_TIME_ZONE = auto()
    BROADCAST_BADGE = auto()
    ADD_VOICEMAIL = auto()
    CHANGE_BADGE = auto()
    UPDATE_BADGE = auto()
    MANAGE_ACCOUNTS = auto()
    LIMIT_RUNNING_PROCESSES = auto()
    SEND_TEXT_MESSAGES = auto()
    MODIFY_TEXT_MESSAGES = auto()
    BIND_GET_INSTALL_REFERRER_SERVICE = auto()
    C2D_MESSAGE = auto()
    USE_CREDENTIALS = auto()
    WRITE_SETTINGS = auto()
    USE_FINGERPRINT = auto()
    CHANGE_WIMAX_STATE = auto()
    MODIFY_AUDIO_SETTINGS = auto()
    MODIFY_PHONE_STATE = auto()
    SET_PREFERRED_APPS = auto()
    MAKE_CALL = auto()
    WRITE_BOOKMARKS_HISTORY = auto()
    WRITE_CALL_LOG = auto()
    MODIFY_OWN_CONTACT = auto()
    SEND_LINUX_SIGNALS = auto()
    # CALL_SELF = auto()

    WRITE = auto()
    READ = auto()
    MEASURE_STORAGE_SPACE = auto()
    READ_BATTERY = auto()
    READ_DICTIONARY = auto()
    READ_GSERVICES = auto()
    BLUETOOTH = auto()
    UPDATE_COUNT = auto()
    BLUETOOTH_ADMIN = auto()
    ENABLE_DEBUGGING = auto()
    READ_SETTINGS = auto()
    CHANGE_WIFI_STATE = auto()
    REROUTE_CALLS = auto()
    RECIEVE_WAP_MESSAGES = auto()
    RECIEVE_TEXT_MESSAGES = auto()
    RECIEVE_MMS = auto()
    MAKE_AND_RECIEVE_SIP_CALLS = auto()
    ERASE_USB_STORAGE = auto()
    RECORD_AUDIO = auto()
    READ_CELL_BROADCAST = auto()
    ACCESS_SERIAL_PORTS = auto()
    CAMERA = auto()
    GET_ACCOUNTS = auto()
    READ_CONTACTS = auto()
    BODY_SENSORS = auto()
    UPDATE_SHORTCUT = auto()
    INSTALL_SHORTCUT = auto()
    READ_CALL_LOG = auto()
    BILLING = auto()
    RECEIVE_BOOT_COMPLETED = auto()
    GET_TASKS = auto()
    READ_TEXT_MESSAGES = auto()
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

big_perm_map = {
    "set preferred apps": Permissions.SET_PREFERRED_APPS,
    "view Wi-Fi connections": Permissions.ACCESS_WIFI_STATE,
    "reroute outgoing calls": Permissions.REROUTE_CALLS,
    "expand/collapse status bar": Permissions.EXPAND_STATUS_BAR,
    "modify global animation speed": Permissions.MANAGE_ANIMATION_SPEED,
    "force background apps to close": Permissions.CLOSE_BG_APPS,
    "read battery statistics": Permissions.READ_BATTERY,
    "read terms you added to the dictionary": Permissions.READ_DICTIONARY,
    "enable app debugging": Permissions.ENABLE_DEBUGGING,
    "measure app storage space": Permissions.MEASURE_STORAGE_SPACE,
    "write web bookmarks and history": Permissions.WRITE_BOOKMARKS_HISTORY,
    "add words to user-defined dictionary": Permissions.WRITE_DISCTIONARY,
    "read call log": Permissions.READ_CALL_LOG,
    "body sensors (like heart rate monitors)": Permissions.BODY_SENSORS,
    "receive text messages (SMS)": Permissions.RECIEVE_TEXT_MESSAGES,
    "read your text messages (SMS or MMS)": Permissions.READ_TEXT_MESSAGES,
    "send SMS messages": Permissions.SEND_TEXT_MESSAGES,
    "modify phone state": Permissions.MODIFY_PHONE_STATE,
    "act as the AccountManagerService": Permissions.MANAGE_ACCOUNTS,
    "make/receive SIP calls": Permissions.MAKE_AND_RECIEVE_SIP_CALLS,
    "modify your own contact card": Permissions.MODIFY_OWN_CONTACT,
    "set time zone": Permissions.SET_TIME_ZONE,
    "edit your text messages (SMS or MMS)": Permissions.MODIFY_TEXT_MESSAGES,
    "write call log": Permissions.WRITE_CALL_LOG,
    "change/intercept network settings and traffic": Permissions.ACCESS_NETWORK_STATE,
    "make app always run": Permissions.FOREGROUND_SERVICE,
    "directly call any phone numbers": Permissions.MAKE_CALL,
    "receive text messages (MMS)": Permissions.RECIEVE_MMS,
    "retrieve system internal state": Permissions.READ_PHONE_STATE,
    "erase USB storage": Permissions.ERASE_USB_STORAGE,
    "add voicemail": Permissions.ADD_VOICEMAIL,
    "Change WiMAX state": Permissions.CHANGE_WIMAX_STATE,
    "read cell broadcast messages": Permissions.READ_CELL_BROADCAST,
    "receive text messages (WAP)": Permissions.RECIEVE_WAP_MESSAGES,
    "send Linux signals to apps": Permissions.SEND_LINUX_SIGNALS,
    "limit number of running processes": Permissions.LIMIT_RUNNING_PROCESSES,
    "access serial ports": Permissions.ACCESS_SERIAL_PORTS,
}


def heuristic(row):
    """
    0: normal
    1: anomaly

    :param row:
    :return:
    """
    keys = [k for k in row.keys() if k in Permissions.__members__.keys()]
    cats = [k for k in row.keys() if k not in ('Key', *Permissions.__members__.keys())][1:]
    # k = cats[0]
    # print("!!!", len(keys), k, cats_old.get(k, 1.0), row[k])
    # print({k: row[k] for k in cats if row[k] if type(row[k]) != int})

    #return int(
    #    sum([Permissions[k].value * row[k] for k in keys]) + 
    #    sum([cats_old.get(k, 1.0) * row[k] for k in cats]) 
    #> 110)
    return int(
        sum([big_perm_map[k].value * row[k] for k in keys]) + 
        sum([cats_old.get(k, 1.0) * float(row[k]) for k in cats]) 
    )


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

# -----------------------

if __name__ == '__main__':
    permissions = ["set preferred apps","view Wi-Fi connections","read terms you added to the dictionary","reroute outgoing calls","directly call phone numbers","read your contacts","expand/collapse status bar","modify global animation speed","control flashlight","force background apps to close","add voicemail","toggle sync on and off","control vibration","read your text messages (SMS or MMS)","access USB storage filesystem","approximate location (network-based)","directly call any phone numbers","read battery statistics","act as the AccountManagerService","limit number of running processes","change your audio settings","record audio","read your own contact card","receive text messages (WAP)","set time zone","write web bookmarks and history","uninstall shortcuts","create accounts and set passwords","Change WiMAX state","access extra location provider commands","access Bluetooth settings","find accounts on the device","disable your screen lock","send sticky broadcast","change/intercept network settings and traffic","full network access","modify system settings","add or remove accounts","read calendar events plus confidential information","body sensors (like heart rate monitors)","mock location sources for testing","send Linux signals to apps","precise location (GPS and network-based)","write call log","change network connectivity","add or modify calendar events and send email to guests without owners' knowledge","modify or delete the contents of your USB storage","Google Play license check","use accounts on the device","delete all app cache data","retrieve running apps","read cell broadcast messages","receive text messages (MMS)","view network connections","run at startup","read Google service configuration","draw over other apps","enable app debugging","connect and disconnect from Wi-Fi","set wallpaper","access serial ports","reorder running apps","read sync settings","erase USB storage","read the contents of your USB storage","receive text messages (SMS)","modify your own contact card","modify your contacts","modify phone state","read your Web bookmarks and history","set an alarm","make/receive SIP calls","add words to user-defined dictionary","pair with Bluetooth devices","close other apps","control Near Field Communication","edit your text messages (SMS or MMS)","take pictures and videos","read sensitive log data","read phone status and identity","change system display settings","prevent device from sleeping","make app always run","retrieve system internal state","install shortcuts","allow Wi-Fi Multicast reception","read call log","send SMS messages","measure app storage space"]
    refs = [k.lower().replace('_', ' ') for k in Permissions.__members__.keys()]

    for p in permissions:
        closest_perm = None
        closest_distance = -1

        for ref in refs:
            d = Levenshtein.distance(p, ref)
            if d < closest_distance or closest_distance == -1:
                closest_perm = ref
                closest_distance = d

        print(f"{p} -[{closest_distance}]-> {closest_perm}")
