import Levenshtein

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import fasttext
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from scipy.spatial.distance import cosine

descriptions = [
    "set preferred apps",
    "read terms you added to the dictionary",
    "reroute outgoing calls",
    "expand/collapse status bar",
    "modify global animation speed",
    "force background apps to close",
    "add voicemail",
    "read your text messages (SMS or MMS)",
    "directly call any phone numbers",
    "read battery statistics",
    "act as the AccountManagerService",
    "limit number of running processes",
    "receive text messages (WAP)",
    "set time zone",
    "write web bookmarks and history",
    "Change WiMAX state",
    "change/intercept network settings and traffic",
    "body sensors (like heart rate monitors)",
    "send Linux signals to apps",
    "write call log",
    "read cell broadcast messages",
    "receive text messages (MMS)",
    "enable app debugging",
    "access serial ports",
    "erase USB storage",
    "receive text messages (SMS)",
    "modify your own contact card",
    "modify phone state",
    "make/receive SIP calls",
    "add words to user-defined dictionary",
    "edit your text messages (SMS or MMS)",
    "make app always run",
    "retrieve system internal state",
    "read call log",
    "send SMS messages",
    "measure app storage space",
]

sample_permissions = [
    "INTERNET",
    "ACCESS_NETWORK_STATE",
    "WAKE_LOCK",
    "WRITE_EXTERNAL_STORAGE",
    "RECEIVE",
    "READ_EXTERNAL_STORAGE",
    "ACCESS_WIFI_STATE",
    "VIBRATE",
    "RECEIVE_BOOT_COMPLETED",
    "BIND_GET_INSTALL_REFERRER_SERVICE",
    "ACCESS_FINE_LOCATION",
    "BILLING",
    "C2D_MESSAGE",
    "ACCESS_COARSE_LOCATION",
    "CAMERA",
    "READ_PHONE_STATE",
    "GET_ACCOUNTS",
    "FOREGROUND_SERVICE",
    "WRITE_SETTINGS",
    "BLUETOOTH",
    "RECORD_AUDIO",
    "READ_CONTACTS",
    "READ_GSERVICES",
    "SYSTEM_ALERT_WINDOW",
    "CHANGE_WIFI_STATE",
    "READ_SETTINGS",
    "READ",
    "MODIFY_AUDIO_SETTINGS",
    "WRITE",
    "BROADCAST_BADGE",
    "UPDATE_SHORTCUT",
    "USE_CREDENTIALS",
    "BLUETOOTH_ADMIN",
    "UPDATE_COUNT",
    "UPDATE_BADGE",
    "USE_FINGERPRINT",
    "CHANGE_BADGE",
    "GET_TASKS",
    "PROVIDER_INSERT_BADGE",
    "READ_APP_BADGE",
    "INSTALL_SHORTCUT",
    "MANAGE_ACCOUNTS",
]

test_map = {
    "ACCESS_CHECKIN_PROPERTIES": "Access Check-in Properties",
    "ACCESS_COARSE_LOCATION": "Access Approximate Location",
    "ACCESS_FINE_LOCATION": "Access Precise Location",
    "ACCESS_LOCATION_EXTRA_COMMANDS": "Access Extra Location Commands",
    "ACCESS_MOCK_LOCATION": "Access Mock Location",
    "ACCESS_NETWORK_STATE": "Access Network State",
    "ACCESS_SURFACE_FLINGER": "Access Surface Flinger",
    "ACCESS_WIFI_STATE": "Access WiFi State",
    "ACCOUNT_MANAGER": "Account Manager",
    "AUTHENTICATE_ACCOUNTS": "Authenticate Accounts",
    "BATTERY_STATS": "Battery Stats",
    "BIND_APPWIDGET": "Bind App Widgets",
    "BIND_DEVICE_ADMIN": "Bind Device Admin",
    "BIND_INPUT_METHOD": "Bind Input Method",
    "BIND_REMOTEVIEWS": "Bind RemoteView",
    "BIND_WALLPAPER": "Bind Wallpaper",
    "BLUETOOTH": "Use Bluetooth",
    "BLUETOOTH_ADMIN": "Bluetooth Admin",
    "BRICK": "Turn Into Brick",
    "BROADCAST_PACKAGE_REMOVED": "Broadcast on App Removal",
    "BROADCAST_SMS": "Broadcast on SMS Receipt",
    "BROADCAST_STICKY": "Sticky Broadcast",
    "BROADCAST_WAP_PUSH": "WAP PUSH Broadcast",
    "CALL_PHONE": "Make Phone Calls",
    "CALL_PRIVILEGED": "Call Privileged",
    "CAMERA": "Camera Access",
    "CHANGE_COMPONENT_ENABLED_STATE": "Change Component State",
    "CHANGE_CONFIGURATION": "Change Configuration",
    "CHANGE_NETWORK_STATE": "Change Network State",
    "CHANGE_WIFI_MULTICAST_STATE": "Change WiFi Multicast State",
    "CHANGE_WIFI_STATE": "Change WiFi State",
    "CLEAR_APP_CACHE": "Clear App Cache",
    "CLEAR_APP_USER_DATA": "Clear User Data",
    "CWJ_GROUP": "Low-Level Access",
    "CELL_PHONE_MASTER_EX": "Cell Phone Master Extension",
    "CONTROL_LOCATION_UPDATES": "Control Location Updates",
    "DELETE_CACHE_FILES": "Delete Cache Files",
    "DELETE_PACKAGES": "Delete Applications",
    "DEVICE_POWER": "Power Management",
    "DIAGNOSTIC": "Application Diagnostic",
    "DISABLE_KEYGUARD": "Disable Keyguard",
    "DUMP": "Dump System Information",
    "EXPAND_STATUS_BAR": "Status Bar Control",
    "FACTORY_TEST": "Factory Test Mode",
    "FLASHLIGHT": "Use Flashlight",
    "FORCE_BACK": "Force Back",
    "GET_ACCOUNTS": "Access Gmail Accounts",
    "GET_PACKAGE_SIZE": "Get App Size",
    "GET_TASKS": "Get Task Information",
    "GLOBAL_SEARCH": "Global Search",
    "HARDWARE_TEST": "Hardware Testing",
    "INJECT_EVENTS": "Inject Events",
    "INSTALL_LOCATION_PROVIDER": "Install Location Provider",
    "INSTALL_PACKAGES": "Install Applications",
    "INTERNAL_SYSTEM_WINDOW": "Internal System Window",
    "INTERNET": "Access Internet",
    "KILL_BACKGROUND_PROCESSES": "Terminate Background Processes",
    "MANAGE_ACCOUNTS": "Manage Accounts",
    "MANAGE_APP_TOKENS": "Manage App Tokens",
    "MTWEAK_USER": "Advanced Permissions",
    "MTWEAK_FORUM": "Community Permissions",
    "MASTER_CLEAR": "Soft Format",
    "MODIFY_AUDIO_SETTINGS": "Modify Audio Settings",
    "MODIFY_PHONE_STATE": "Modify Phone State",
    "MOUNT_FORMAT_FILESYSTEMS": "Format File Systems",
    "MOUNT_UNMOUNT_FILESYSTEMS": "Mount File Systems",
    "NFC": "Allow NFC Communication",
    "PERSISTENT_ACTIVITY": "Persistent Activity",
    "PROCESS_OUTGOING_CALLS": "Process Outgoing Calls",
    "READ_CALENDAR": "Read Calendar Events",
    "READ_CONTACTS": "Read Contacts",
    "READ_FRAME_BUFFER": "Screenshot",
    "READ_HISTORY_BOOKMARKS": "Read Bookmarks and History",
    "READ_INPUT_STATE": "Read Input State",
    "READ_LOGS": "Read System Logs",
    "READ_PHONE_STATE": "Read Phone State",
    "READ_SMS": "Read SMS Content",
    "READ_SYNC_SETTINGS": "Read Sync Settings",
    "READ_SYNC_STATS": "Read Sync Stats",
    "REBOOT": "Reboot Device",
    "RECEIVE_BOOT_COMPLETED": "Auto-Run on Boot",
    "RECEIVE_MMS": "Receive MMS",
    "RECEIVE_SMS": "Receive SMS",
    "RECEIVE_WAP_PUSH": "Receive Wap Push",
    "RECORD_AUDIO": "Record Audio",
    "REORDER_TASKS": "Reorder System Tasks",
    "RESTART_PACKAGES": "End System Tasks",
    "SEND_SMS": "Send SMS",
    "SET_ACTIVITY_WATCHER": "Set Activity Watcher",
    "SET_ALARM": "Set Alarm Reminder",
    "SET_ALWAYS_FINISH": "Set Always Finish",
    "SET_ANIMATION_SCALE": "Set Animation Scale",
    "SET_DEBUG_APP": "Set Debug App",
    "SET_ORIENTATION": "Set Screen Orientation",
    "SET_PREFERRED_APPLICATIONS": "Set Preferred Applications",
    "SET_PROCESS_LIMIT": "Set Process Limit",
    "SET_TIME": "Set System Time",
    "SET_TIME_ZONE": "Set System Timezone",
    "SET_WALLPAPER": "Set Desktop Wallpaper",
    "SET_WALLPAPER_HINTS": "Set Wallpaper Suggestions",
    "SIGNAL_PERSISTENT_PROCESSES": "Send Persistent Process Signals",
    "STATUS_BAR": "Status Bar Control",
    "SUBSCRIBED_FEEDS_READ": "Access Subscribed Content",
    "SUBSCRIBED_FEEDS_WRITE": "Write Subscribed Content",
    "SYSTEM_ALERT_WINDOW": "Show System Windows",
    "UPDATE_DEVICE_STATS": "Update Device Status",
    "USE_CREDENTIALS": "Use Credentials",
    "USE_SIP": "Use SIP Video",
    "VIBRATE": "Use Vibration",
    "WAKE_LOCK": "Wake Lock",
    "WRITE_APN_SETTINGS": "Write GPRS Access Point Settings",
    "WRITE_CALENDAR": "Write Calendar Events",
    "WRITE_CONTACTS": "Write Contacts",
    "WRITE_EXTERNAL_STORAGE": "Write External Storage",
    "WRITE_GSERVICES": "Write Google Map Data",
    "WRITE_HISTORY_BOOKMARKS": "Write Bookmarks and History",
    "WRITE_SECURE_SETTINGS": "Read and Write Secure Settings",
    "WRITE_SETTINGS": "Read and Write System Settings",
    "WRITE_SMS": "Write SMS",
}
test_map = {k: test_map[k].lower() for k in test_map}

descriptions = list(test_map.values())
sample_permissions = list(test_map.keys())

descriptions = [d.lower() for d in descriptions]

# vectorizer = TfidfVectorizer()
# tfidf_matrix = vectorizer.fit_transform(descriptions)

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
fasttext_model = fasttext.load_model('/home/me/Downloads/cc.en.300.bin')

token_map = {
    "fine": "precise",
    "packag": "app",
    "package": "app",
    "application": "app",
    "get": "acces", # ?
    "zone": "timezone",
    "kill": "close",
    #"receive": "read",
    "stat": "statistic",
    #"get": "read",
    #"set": "write",
}

def tokenize(word: str) -> str:
    word = ''.join([c for c in word if c.isalnum()])
    if word.endswith('es'):
        word = word[:-2]
    if word.endswith('s'):
        word = word[:-1]
    if word.endswith('ing'):
        word = word[:-3]
    if word in token_map:
        word = token_map[word]
    return word

class WordImportanceStorage:
    def __init__(self, docs: [str]):
        words = set()
        for doc in docs:
            for w in doc.split():
                words.add(tokenize(w))
        
        self.word_importance_map: {str: float} = {w: 0 for w in words}
        for doc in docs:
            ws = [tokenize(w) for w in doc.split()]
            if w in ws:
               self.word_importance_map[w] += 1
        
        n_docs = len(docs)
        self.word_importance_map = {k: 2-self.word_importance_map[k]/n_docs for k in self.word_importance_map}

    def get_importance(self, w: str) -> float:
        return self.word_importance_map.get(w, 1)

store = WordImportanceStorage(descriptions)

def find_closest_description(permission_key, dist_func):
    permission_key = permission_key.replace('_', ' ').lower()
    
    best_match = None
    best_distance = float('inf')
    
    for description in descriptions:
        distance = dist_func(permission_key, description)
        
        if distance < best_distance:
            best_match = description
            best_distance = distance
            
    return best_match, best_distance 

# Function to get the average vector representation of a sentence or phrase using FastText
def get_vector(text):
    words = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    words = [word for word in words if word not in stopwords.words('english') and word.isalnum()]
    
    if not words:
        return np.zeros(300)  # Return a zero vector if no valid words in the text
    
    vectors = [fasttext_model.get_word_vector(word) for word in words if word in fasttext_model]
    
    if not vectors:
        return np.zeros(300)  # Return a zero vector if no valid embeddings
    
    return np.mean(vectors, axis=0)  # Average word vectors


# Function to calculate semantic distance between permission_key and description
def semantic_distance(permission_key, description):
    permission_vector = get_vector(permission_key)
    description_vector = get_vector(description)
    
    # Calculate cosine similarity (1 - cosine distance)
    return cosine(permission_vector, description_vector)

def simple_token_inclusion_distance(permission, description):
    desc_words = [tokenize(w) for w in description.lower().split()]
    return 1 - len({p for p in permission.split() if tokenize(p) in desc_words}) / len(permission.split())

def token_inclusion_distance_with_word_importance(permission, description):
    desc_words = [tokenize(w) for w in description.lower().split()]
    n_words = len({p for p in permission.split() if tokenize(p) in desc_words})
    importance = sum([store.get_importance(tokenize(p)) for p in permission.split() if tokenize(p) in desc_words])
    # if importance != n_words: print("nope")
    return 1 - ((n_words*0.5 + importance*0.5) / len(permission.split()))
    # return 1 - importance / len(permission.split())

def cosine_distance(permission, description):
    """
    A distance measure using cosine similarity with the TF-IDF index.
    We return (1 - cosine similarity) because we're aiming for a "distance".
    """
    permission_vector = vectorizer.transform([permission.lower()])
    description_vector = tfidf_matrix[descriptions.index(description)]
    return 1 - cosine_similarity(permission_vector, description_vector)[0][0]

def jaccard_similarity(permission, description):
    set1 = {tokenize(w) for w in permission.lower().split()}
    set2 = {tokenize(w) for w in description.lower().split()}

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
     
    return 1 - intersection / union

if __name__ == "__main__":
    dist_funcs = (
        # Levenshtein.distance, 
        simple_token_inclusion_distance, 
        # cosine_distance,
        # lambda perm, desc: 0.5*simple_token_inclusion_distance(perm, desc) + 0.5*cosine_distance(perm, desc),
        token_inclusion_distance_with_word_importance,
        jaccard_similarity,
        semantic_distance,
    )
    for dist_func in dist_funcs:
        errors = 0
        for permission_key in sample_permissions:
            best_description, distance = find_closest_description(permission_key, dist_func)
            
            if test_map[permission_key] != best_description:
                print(f"ERROR for '{permission_key}' [{distance}]: got '{best_description}', expected '{test_map[permission_key]}'")
                errors += 1

        # print(f"[{dist_func.__name__}] ERRORS: {100*errors/len(sample_permissions)}%")
        print(f"[{dist_func.__name__}] ERRORS: ({errors}) {100*errors/len(sample_permissions):.3f}%")

    print(len(sample_permissions))