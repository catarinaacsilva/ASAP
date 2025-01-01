from abc import ABC, abstractmethod 
import scraping.category_to_csv as category_to_csv 
import Levenshtein
import tensorflow as tf
import numpy as np
import json

import fasttext
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from scipy.spatial.distance import cosine

from .vae import VAE, Sampling

print("Loading Fast Text model...")
fasttext_model = fasttext.load_model('/home/me/Downloads/cc.en.300.bin')
print("Done!")

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
    "you": "user",
}

def tokenize(word: str) -> str:
    word = "".join([c if c.isalnum() else " " for c in word])
    if word.endswith('es'):
        word = word[:-2]
    if word.endswith('s'):
        word = word[:-1]
    if word.endswith('ing'):
        word = word[:-3]
    if word in token_map:
        word = token_map[word]
    return word

def get_vector(text):
    words = word_tokenize(text.lower())
    words = [word for word in words if word not in stopwords.words('english') and word.isalnum()]
    
    if not words:
        return np.zeros(300)  # Return a zero vector if no valid words in the text
    
    vectors = [fasttext_model.get_word_vector(word) for word in words if word in fasttext_model]
    
    if not vectors:
        return np.zeros(300)  # Return a zero vector if no valid embeddings
    
    return np.mean(vectors, axis=0)


def semantic_distance(permission_key, description):
    permission_vector = get_vector(permission_key)
    description_vector = get_vector(description)
    
    similarity = cosine(permission_vector, description_vector)
    return similarity # 1 - ((similarity + 1)/2)

def simple_token_inclusion_distance(permission, description):
    desc_words = [tokenize(w) for w in description.lower().split()]
    return 1 - len({p for p in permission.split() if tokenize(p) in desc_words}) / len(permission.split())

def jaccard_similarity(permission, description):
    set1 = {tokenize(w) for w in permission.lower().split()}
    set2 = {tokenize(w) for w in description.lower().split()}

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
     
    return 1 - intersection / union

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

    def token_inclusion_distance_with_word_importance(self, permission, description):
        desc_words = [tokenize(w) for w in description.lower().split()]
        n_words = len({p for p in permission.split() if tokenize(p) in desc_words})
        importance = sum([self.get_importance(tokenize(p)) for p in permission.split() if tokenize(p) in desc_words])

        nw_w = 0.9
        i_w = 1 - nw_w

        return 1 - ((n_words*nw_w + importance*i_w) / len(permission.split()))

# dist_func = Levenshtein.distance
# dist_func = simple_token_inclusion_distance
# dist_func = jaccard_similarity
dist_func = semantic_distance

class Model(ABC):
    def __init__(self, model_path: str, permissions: [str], categories: [str], swap_order: bool=False):
        self.__model_path = model_path
        self.name = model_path.split('/')[1].split('.')[0]
        self.__header = [*permissions, *categories] if not swap_order else [*categories, *permissions]
        self._permissions = permissions
        self._categories = categories
        self.__autoencoder = tf.keras.models.load_model(self.__model_path, custom_objects={'VAE': VAE, 'Sampling': Sampling}, compile=False)

        with open("out/thresholds.json") as f:
            data = json.loads(f.read())
            self.__thresholds = data[self.name]

    @abstractmethod
    def map_permission(self, permission: str) -> str:
        pass

    @abstractmethod
    def map_category(self, category: str) -> str:
        pass

    def get_apk_features(self, apk_permissions: [str], apk_categories: [str]) -> [str]:
        permissions = [p_mapped for p in apk_permissions if (p_mapped := self.map_permission(p)) is not None]
        categories = [c_mapped for c in apk_categories if (c_mapped := self.map_category(c)) is not None]
        perms_cats = [*permissions, *categories]

        return perms_cats

    def analyse_apk(self, apk_permissions: [str], apk_categories: [str]) -> bool:
        permissions = [p_mapped for p in apk_permissions if (p_mapped := self.map_permission(p)) is not None]
        categories = [c_mapped for c in apk_categories if (c_mapped := self.map_category(c)) is not None]
        perms_cats = [*permissions, *categories]

        encoded = [pc in perms_cats for pc in self.__header]

        X_test = np.array(encoded, dtype=np.float32).reshape(1, len(encoded))
        reconstructions = self.__autoencoder.predict(X_test)

        mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)
        mae = np.mean(np.abs(X_test - reconstructions), axis=1)

        thr = self.__thresholds["iso-data"]
        y_pred = mae > thr
        return y_pred[0]
    

class ExodusModel(Model):
    def __init__(self, model_path: str):
        self.category_map = {
            "games": "x0_Arcade & Action",
            # "learning": "x0_Books & Reference",
            # "games": "x0_Brain & Puzzle",
            "office": "x0_Business",
            # "games": "x0_Cards & Casino",
            # "games": "x0_Casual",
            # "multimedia": "x0_Comics",
            # "social media": "x0_Communication",
            "learning": "x0_Education",
            # "games": "x0_Entertainment",
            # "office": "x0_Finance",
            "health": "x0_Health & Fitness",
            # "learning": "x0_Libraries & Demo",
            # "sports": "x0_Lifestyle",
            "multimedia": "x0_Media & Video",
            # "health": "x0_Medical",
            # "multimedia": "x0_Music & Audio",
            # "learning": "x0_News & Magazines",
            "customization": "x0_Personalization",
            # "multimedia": "x0_Photography",
            "office": "x0_Productivity",
            # "games": "x0_Racing",
            "shopping": "x0_Shopping",
            "social media": "x0_Social",
            "sports": "x0_Sports",
            # "games": "x0_Sports Games",
            # "customization": "x0_Tools",
            # "social media": "x0_Transportation",
            # "social media": "x0_Travel & Local",
            # "office": "x0_Weather",
        }
        permissions = [
            "access drm content",
            "access email provider data",
            "access all system downloads",
            "access download manager",
            "advanced download manager functions",
            "audio file access",
            "install drm content",
            "modify google service configuration",
            "modify google settings",
            "move application resources",
            "read google settings",
            "send download notifications",
            "voice search shortcuts",
            "access surfaceflinger",
            "access checkin properties",
            "access the cache filesystem",
            "access to passwords for google accounts",
            "act as an account authenticator",
            "bind to a wallpaper",
            "bind to an input method",
            "change screen orientation",
            "coarse (network-based) location",
            "control location update notifications",
            "control system backup and restore",
            "delete applications",
            "delete other applications' caches",
            "delete other applications' data",
            "directly call any phone numbers",
            "directly install applications",
            "disable or modify status bar",
            "discover known accounts",
            "display unauthorized windows",
            "enable or disable application components",
            "force application to close",
            "force device reboot",
            "full internet access",
            "interact with a device admin",
            "manage application tokens",
            "mock location sources for testing",
            "modify battery statistics",
            "modify secure system settings",
            "modify the google services map",
            "modify/delete usb storage contents modify/delete sd card contents",
            "monitor and control all application launching",
            "partial shutdown",
            "permanently disable device",
            "permission to install a location provider",
            "power device on or off",
            "press keys and control buttons",
            "prevent app switches",
            "read frame buffer",
            "read instant messages",
            "read phone state and identity",
            "record what you type and actions you take",
            "reset system to factory defaults",
            "run in factory test mode",
            "set time",
            "set wallpaper size hints",
            "start im service",
            "update component usage statistics",
            "write contact data",
            "write instant messages",
            "enable application debugging",
            "limit number of running processes",
            "make all background applications close",
            "send linux signals to applications",
            "change your audio settings",
            "control flashlight",
            "control vibrator",
            "record audio",
            "take pictures and videos",
            "test hardware",
            "broadcast data messages to applications",
            "control near field communication",
            "create bluetooth connections",
            "download files without notification",
            "full internet access",
            "make/receive internet calls",
            "receive data from internet",
            "view wi-fi state",
            "view network state",
            "intercept outgoing calls",
            "modify phone state",
            "read phone state and identity",
            "directly call phone numbers",
            "send sms messages",
            "modify/delete usb storage contents modify/delete sd card contents",
            "allow wi-fi multicast reception",
            "automatically start at boot",
            "bluetooth administration",
            "change wi-fi state",
            "change background data usage setting",
            "change network connectivity",
            "change your ui settings",
            "delete all application cache data",
            "disable keylock",
            "display system-level alerts",
            "expand/collapse status bar",
            "force stop other applications",
            "format external storage",
            "kill background processes",
            "make application always run",
            "measure application storage space",
            "modify global animation speed",
            "modify global system settings",
            "mount and unmount filesystems",
            "prevent device from sleeping",
            "read subscribed feeds",
            "read sync settings",
            "read sync statistics",
            "read/write to resources owned by diag",
            "reorder running applications",
            "retrieve running applications",
            "send package removed broadcast",
            "send sticky broadcast",
            "set preferred applications",
            "set time zone",
            "set wallpaper",
            "set wallpaper size hints",
            "write access point name settings",
            "write subscribed feeds",
            "write sync settings",
            "blogger",
            "google app engine",
            "google docs",
            "google finance",
            "google maps",
            "google spreadsheets",
            "google voice",
            "google mail",
            "picasa web albums",
            "youtube",
            "youtube usernames",
            "access all google services",
            "access other google services",
            "act as an account authenticator",
            "act as the accountmanagerservice",
            "contacts data in google accounts",
            "discover known accounts",
            "manage the accounts list",
            "read google service configuration",
            "use the authentication credentials of an account",
            "view configured accounts",
            "access extra location provider commands",
            "coarse (network-based) location",
            "fine (gps) location",
            "mock location sources for testing",
            "read email attachments",
            "send gmail",
            "edit sms or mms",
            "modify gmail",
            "read gmail",
            "read gmail attachment previews",
            "read sms or mms",
            "read instant messages",
            "receive mms",
            "receive sms",
            "receive wap",
            "send sms-received broadcast",
            "send wap-push-received broadcast",
            "write instant messages",
            "add or modify calendar events and send email to guests",
            "choose widgets",
            "read browser's history and bookmarks",
            "read calendar events",
            "read contact data",
            "read sensitive log data",
            "read user defined dictionary",
            "retrieve system internal state",
            "set alarm in alarm clock",
            "write browser's history and bookmarks",
            "write contact data",
            "write to user defined dictionary", 
        ]
        categories = [
            "x0_Arcade & Action",
            "x0_Books & Reference",
            "x0_Brain & Puzzle",
            "x0_Business",
            "x0_Cards & Casino",
            "x0_Casual",
            "x0_Comics",
            "x0_Communication",
            "x0_Education",
            "x0_Entertainment",
            "x0_Finance",
            "x0_Health & Fitness",
            "x0_Libraries & Demo",
            "x0_Lifestyle",
            "x0_Media & Video",
            "x0_Medical",
            "x0_Music & Audio",
            "x0_News & Magazines",
            "x0_Personalization",
            "x0_Photography",
            "x0_Productivity",
            "x0_Racing",
            "x0_Shopping",
            "x0_Social",
            "x0_Sports",
            "x0_Sports Games",
            "x0_Tools",
            "x0_Transportation",
            "x0_Travel & Local",
            "x0_Weather",
        ]
        super().__init__(model_path, permissions, categories)

    def map_category(self, category: str) -> str:
        return self.category_map.get(category, None)
    
    def map_permission(self, permission: str) -> str:
        permission_key = permission.replace('_', ' ').lower()
        
        best_match = None
        best_distance = float('inf')
        
        for perm in self._permissions:
            distance = dist_func(permission_key, perm.lower())
            
            if distance < best_distance:
                best_match = perm
                best_distance = distance
                
        if best_distance < 0.5:
           #  print(f"PERM [{best_distance:.3f}] {permission} -> {best_match}")
            return best_match
        else: 
            return None


class APDModel(Model):
    def __init__(self, model_path: str):
        permissions = [
            "OTHER_PERMISSIONS",
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
        categories = [
            "design",
            "multi player",
            "video downloader",
            "clicker/idle",
            "keyboards",
            "tennis",
            "weather",
            "renovate & decorat",
            "piano",
            "e commerce",
            "visual assistance",
            "sniper",
            "health & fitness",
            "physics",
            "adv",
            "shopping",
            "mathematics",
            "social media",
            "wallpaper",
            "personalisation",
            "learning",
            "bang dream",
            "heroes",
            "language",
            "pixel art",
            "performance",
            "artillery shooter",
            "customization",
            "beauty",
            "libraries & demo",
            "virtual pet",
            "happy diwali",
            "acg",
            "real time",
            "kids",
            "drifting",
            "mini-games",
            "ai",
            "shooting rpg",
            "multimedia",
            "super hero",
            "train",
            "fight",
            "strategy rpg",
            "kwaii",
            "football",
            "file managers",
            "coaching",
            "download tool",
            "ball",
            "kart",
            "privacy",
            "galgame",
            "player",
            "baby",
            "lifestyle",
            "office",
            "hearing assistance",
            "maplestory",
            "games",
            "learning disability",
            "idol",
            "play to earn",
            "third person",
            "parenting",
            "cross-platform",
            "personalization",
            "speed test",
            "dinosaurs",
            "life",
            "translation",
            "exploration",
            "screen casting",
            "sports",
            "pool",
            "cv",
            "doctor",
            "rummy",
        ]
        super().__init__(model_path, permissions, categories, swap_order=True)

    def map_category(self, category: str) -> str:
        category = category.lower()
        return "games" if category in category_to_csv.games else \
            "learning" if category in category_to_csv.learning else \
            "social media" if category in category_to_csv.social_media else \
            "sports" if category in category_to_csv.sports else \
            "multimedia" if category in category_to_csv.multimedia else \
            "health" if category in category_to_csv.health else \
            "office" if category in category_to_csv.office else \
            "customization" if category in category_to_csv.customization else \
            "shopping" if category in category_to_csv.shopping else \
            category if category in self._categories else \
            None

    def map_permission(self, permission: str) -> str:
        return permission if permission in self._permissions else "OTHER_PERMISSIONS"
    

class ABigModel(Model):
    def __init__(self, model_path: str):
        perms = [s.lower() for s in [
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
        ]]
        cats = [
           "detective",
           "super hero",
           "girls",
           "multiple characters",
           "norse mythology",
           "__error__",
           "draughts",
           "p v e",
           "bl",
           "player",
           "multimedia",
           "drums",
           "shopping",
           "livestreaming video games",
           "location-based",
           "nail salon",
           "crafting",
           "hearing assistance",
           "calling",
           "superstar smtown",
           "sony",
           "video sharing",
           "office",
           "learning",
           "stg",
           "sports",
           "renovate & decorat",
           "cv",
           "teen patti",
           "social media",
           "health",
           "lifestyle",
           "acg",
           "customization",
           "uta no☆prince-sama",
           "adv",
           "games",
        ]
        # print("->", len(perms), len(cats))
        super().__init__(model_path, perms, cats)


    def map_category(self, category: str) -> bool:
        category = category.lower()
        mapped = "games" if category in category_to_csv.games else \
            "learning" if category in category_to_csv.learning else \
            "social media" if category in category_to_csv.social_media else \
            "sports" if category in category_to_csv.sports else \
            "multimedia" if category in category_to_csv.multimedia else \
            "health" if category in category_to_csv.health else \
            "office" if category in category_to_csv.office else \
            "customization" if category in category_to_csv.customization else \
            "shopping" if category in category_to_csv.shopping else \
            category if category in self._categories else \
            None
        # print(f"CAT {category} -> {mapped}")
        return mapped

    def map_permission(self, permission: str) -> str:
        permission_key = permission.replace('_', ' ').lower()
        
        best_match = None
        best_distance = float('inf')
        
        for perm in self._permissions:
            distance = dist_func(permission_key, perm.lower())
            
            if distance < best_distance:
                best_match = perm
                best_distance = distance

        # return best_match
        if best_distance < 0.5:
            # print(f"PERM [{best_distance:.3f}] {permission} -> {best_match}")
            return best_match
        else:
            return None
