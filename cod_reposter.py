import os
import re
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl import types

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


# ============================================================
# ENV HELPERS - برای Railway و اجرای لوکال
# ============================================================

def get_env_value(name: str, default=None):
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value


def get_env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# CONFIG - مقادیر اصلی
# ============================================================

API_ID = get_env_int("API_ID", 25721698)

# به خاطر امنیت، مقدار API_HASH را اینجا دوباره چاپ نکردم.
# روی سیستم خودت می‌توانی مقدار قبلی خودت را جایگزین PUT_YOUR_API_HASH_HERE کنی.
# روی Railway بهتره API_HASH را داخل Variables بگذاری.
API_HASH = get_env_value("API_HASH", "PUT_YOUR_API_HASH_HERE")

SESSION_NAME = get_env_value("SESSION_NAME", "my_telegram_account")

# برای Railway:
# مقدار TELEGRAM_SESSION_STRING را از generate_session.py بگیر و داخل Railway Variables بگذار.
TELEGRAM_SESSION_STRING = get_env_value("TELEGRAM_SESSION_STRING", "")

# کانال مبدا A
SOURCE_CHANNEL = get_env_value("SOURCE_CHANNEL", "@channelAtes")

# کانال مقصد B
DEST_CHANNEL = get_env_value("DEST_CHANNEL", "@channelBtest")

# حالت اجرا:
# "RUN" برای اجرای اصلی
# "EMOJI_IDS" برای گرفتن document_id ایموجی‌های پرمیوم از Saved Messages
RUN_MODE = get_env_value("RUN_MODE", "RUN")

ONLY_VIDEO = True
USE_TRANSLATOR = True
SKIP_IF_DESCRIPTION_EMPTY = True

# کپشن ویدیو در تلگرام محدودیت دارد.
# اگر کپشن طولانی شد، فقط Description کوتاه می‌شود.
MAX_CAPTION_LENGTH = 1024

# برای Railway اگر Volume ساختی، DATA_DIR را بگذار /data
DATA_DIR = get_env_value("DATA_DIR", ".")

TEMP_DOWNLOAD_DIR = os.path.join(DATA_DIR, "temp_downloads")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_messages.json")

# شمارنده اکانت
ACCOUNT_COUNTER_START = get_env_int("ACCOUNT_COUNTER_START", 1882)
ACCOUNT_COUNTER_FILE = os.path.join(DATA_DIR, "account_counter.json")


# ============================================================
# LINKS - لینک‌های آبی فرم خودت
# ============================================================
# اگر لینکی نمی‌خواهی، مقدار را خالی بگذار: ""

GROUP_USERNAME = "@M_COD"
GROUP_URL = "https://t.me/M_COD"

MM_USERNAME = "@Reall"
MM_URL = "https://t.me/Reall"

TERMS_URL = "https://t.me/CODProtect"
REVIEWS_URL = "https://t.me/CODVC"
HOW_IT_WORKS_URL = "https://t.me/CODProtect/119"
WEBSITE_URL = "https://codbuysell.vercel.app/"
AD_POSTING_BOT_URL = "https://t.me/COD_ADBOT"

BUY_NOW_URL = "https://t.me/Reall"
SELL_YOUR_ACCOUNT_URL = "https://t.me/Reall"

COD_BUY_SELL_URL = "https://t.me/COD_BUY_SELL"


# ============================================================
# QUOTE SETTINGS
# ============================================================

QUOTE_HASHTAGS = True
QUOTE_ACTION_BUTTONS = True


# ============================================================
# CUSTOM PREMIUM EMOJI IDS
# ============================================================

CUSTOM_EMOJI_IDS = {
    "red_triangle": 5972290052451994935,      # 🔻
    "green_circle": 5215685881989442149,      # 🟢
    "link": 5215441850537618106,              # 🔗
    "outbox": 5873225338984599714,            # 📤
    "money": 5213094908608392768,             # 💰
    "chat": 5872886929921413168,              # 💬
    "person": 5870994129244131212,            # 👤
    "card": 6041815299412463725,              # 💳
    "memo": 5960551395730919906,              # 📝
    "question": 5872996816659681395,          # ❓
    "globe": 5870718740236079262,             # 🌐
    "robot": 5985780596268339498,             # 🤖

    # اگر کنار MM مثل عکس یک ایموجی خاص داری، اینجا بگذار
    "mm_badge": 6041815299412463725,
}


# ============================================================
# CALL OF DUTY LOGO - 12 CUSTOM EMOJI PIECES
# ============================================================

COD_LOGO_FALLBACK_EMOJI = "🫧"

COD_LOGO_CUSTOM_EMOJI_IDS = [
    5170359296818414550,  # piece 01 - بالا، چپ به راست
    5170609925340005280,  # piece 02
    5170162050445345727,  # piece 03
    5172460553733408202,  # piece 04
    5172741483249271690,  # piece 05
    5170391461828494206,  # piece 06

    5170674117921211510,  # piece 07 - پایین، چپ به راست
    5170201894856951345,  # piece 08
    5170501662099374770,  # piece 09
    5172766699002266296,  # piece 10
    5172551052989301894,  # piece 11
    5170214878543086497,  # piece 12
]


# ============================================================
# FORM SETTINGS
# ============================================================

ACCOUNT_NUMBER_TAG = "#account_number"

HASHTAGS = "#COD #CODBUY #CODSELL\n#CALLOFDUTY #CALL_OF_DUTY\n#ACCOUNTCOD"

ACCOUNT_PRICE_TEXT = "DM for price"


# ============================================================
# SOURCE CAPTION FILTER SETTINGS
# ============================================================

DESCRIPTION_MARKERS = [
    "توضیحات اکانت",
    "توضیحات",
    "📄 توضیحات اکانت",
    "📄 توضیحات",
]

FORBIDDEN_LINE_KEYWORDS = [
    # فارسی
    "قیمت",
    "تومان",
    "خرید",
    "فروش",
    "جهت خرید",
    "آیدی",
    "ایدی",
    "واسطه",
    "قانونی",
    "نماد اعتماد",

    "اکتیویژن",
    "اکتی",
    "فیس",
    "فیسبوک",
    "دیس",
    "دیسیبل",
    "لاین",
    "اپل",
    "لینک",
    "لینک شده",

    # انگلیسی
    "price",
    "buy",
    "sell",
    "activision",
    "acti",
    "facebook",
    "fb",
    "apple",
    "line",
    "linked",
    "link",
    "disabled",
    "disable",
]

END_SECTION_KEYWORDS = [
    "قیمت",
    "تومان",
    "جهت خرید",
    "آیدی",
    "ایدی",
    "واسطه",
    "خرید سی پی",
    "خرید cp",
    "💵",
    "💸",
]


# ============================================================
# BASIC UTILITIES
# ============================================================

def parse_entity_ref(value):
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        return value

    return value


SOURCE_ENTITY = parse_entity_ref(SOURCE_CHANNEL)
DEST_ENTITY = parse_entity_ref(DEST_CHANNEL)


def ensure_parent_dir(file_path: str) -> None:
    directory = os.path.dirname(file_path)

    if directory:
        os.makedirs(directory, exist_ok=True)


def load_processed_ids() -> set:
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()


def save_processed_ids(processed_ids: set) -> None:
    ensure_parent_dir(PROCESSED_FILE)

    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)


def load_account_counter() -> int:
    """
    شماره بعدی اکانت را از فایل می‌خواند.
    اگر فایل وجود نداشت، از ACCOUNT_COUNTER_START شروع می‌کند.
    """
    if not os.path.exists(ACCOUNT_COUNTER_FILE):
        return ACCOUNT_COUNTER_START

    try:
        with open(ACCOUNT_COUNTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            value = int(data.get("next_account_number", ACCOUNT_COUNTER_START))
            return value
    except Exception:
        return ACCOUNT_COUNTER_START


def save_account_counter(next_number: int) -> None:
    """
    شماره بعدی اکانت را ذخیره می‌کند.
    """
    ensure_parent_dir(ACCOUNT_COUNTER_FILE)

    with open(ACCOUNT_COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"next_account_number": int(next_number)},
            f,
            ensure_ascii=False,
            indent=2,
        )


def increment_account_counter(current_number: int) -> None:
    """
    بعد از ارسال موفق پست، شماره را یکی زیاد می‌کند.
    """
    save_account_counter(int(current_number) + 1)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": " ",
        "\u200f": "",
        "\u200e": "",
        "\ufeff": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_source_mentions_hashtags_links(text: str) -> str:
    text = re.sub(r"@\w{3,}", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"https?://\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"t\.me/\S+", "", text, flags=re.IGNORECASE)

    return normalize_text(text)


def contains_forbidden_keyword(line: str) -> bool:
    low = line.lower()
    return any(keyword.lower() in low for keyword in FORBIDDEN_LINE_KEYWORDS)


def is_uid_line(line: str) -> bool:
    low = line.lower()

    if "uid" in low:
        return True

    if re.search(r"\d{10,}", line):
        return True

    return False


def is_end_section_line(line: str) -> bool:
    low = line.lower()

    if is_uid_line(line):
        return True

    return any(keyword.lower() in low for keyword in END_SECTION_KEYWORDS)


def clean_description_line(line: str) -> str:
    line = normalize_text(line)

    if not line:
        return ""

    if contains_forbidden_keyword(line):
        return ""

    line = remove_source_mentions_hashtags_links(line)

    return normalize_text(line)


def extract_description_from_source_caption(caption: str) -> str:
    caption = normalize_text(caption)

    if not caption:
        return ""

    lines = caption.splitlines()

    start_index: Optional[int] = None
    seed_line = ""

    for i, line in enumerate(lines):
        clean_line = normalize_text(line)

        for marker in DESCRIPTION_MARKERS:
            if marker in clean_line:
                start_index = i + 1

                after_marker = clean_line.split(marker, 1)[1].strip()
                after_marker = after_marker.strip(":：-–—| ")

                if after_marker:
                    seed_line = after_marker

                break

        if start_index is not None:
            break

    if start_index is None:
        return ""

    description_lines: List[str] = []

    if seed_line:
        cleaned_seed = clean_description_line(seed_line)
        if cleaned_seed:
            description_lines.append(cleaned_seed)

    for line in lines[start_index:]:
        line = normalize_text(line)

        if not line:
            continue

        if is_end_section_line(line):
            break

        cleaned = clean_description_line(line)

        if cleaned:
            description_lines.append(cleaned)

    result = "\n".join(description_lines)
    result = normalize_text(result)

    result_lines = [line.strip() for line in result.splitlines() if line.strip()]

    return "\n".join(result_lines).strip()


def translate_to_english(text: str) -> str:
    if not text:
        return ""

    if not USE_TRANSLATOR:
        return text

    if GoogleTranslator is None:
        print("Package deep-translator نصب نیست. متن بدون ترجمه ارسال می‌شود.")
        return text

    try:
        translator = GoogleTranslator(source="auto", target="en")
        translated_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                translated_lines.append("")
                continue

            try:
                translated = translator.translate(line)
                translated_lines.append(translated)
            except Exception:
                translated_lines.append(line)

        return normalize_text("\n".join(translated_lines))

    except Exception as e:
        print(f"Translation error: {e}")
        return text


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def substring_by_utf16(text: str, offset: int, length: int) -> str:
    data = text.encode("utf-16-le")
    part = data[offset * 2:(offset + length) * 2]
    return part.decode("utf-16-le", errors="ignore")


def is_valid_url(url: str) -> bool:
    if not url:
        return False

    url = url.strip()

    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("tg://")
    )


# ============================================================
# CAPTION BUILDER WITH CUSTOM EMOJI, LINKS, QUOTES
# ============================================================

class CaptionBuilder:
    def __init__(self):
        self.text_parts: List[str] = []
        self.entities: List[object] = []

    @property
    def text(self) -> str:
        return "".join(self.text_parts)

    def append(self, value: str) -> None:
        self.text_parts.append(value)

    def append_custom_emoji(self, emoji: str, key: str) -> None:
        document_id = int(CUSTOM_EMOJI_IDS.get(key, 0) or 0)
        self.append_custom_emoji_by_id(emoji, document_id)

    def append_custom_emoji_by_id(self, emoji: str, document_id: int) -> None:
        offset = utf16_length(self.text)
        length = utf16_length(emoji)

        self.text_parts.append(emoji)

        if document_id:
            self.entities.append(
                types.MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=int(document_id),
                )
            )

    def append_text_link(self, text: str, url: str = "") -> None:
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

    def append_blockquote(self, text: str, url: str = "") -> None:
        """
        متن را به حالت Quote / Blockquote اضافه می‌کند.
        اگر url هم داده شود، همان متن لینک‌دار هم می‌شود.
        """
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

        blockquote_class = getattr(types, "MessageEntityBlockquote", None)

        if blockquote_class is not None:
            try:
                self.entities.append(
                    blockquote_class(
                        offset=offset,
                        length=length,
                    )
                )
            except TypeError:
                try:
                    self.entities.append(
                        blockquote_class(
                            offset=offset,
                            length=length,
                            collapsed=False,
                        )
                    )
                except Exception:
                    pass

    def append_cod_logo(self) -> None:
        """
        ۱۲ کاستوم ایموجی لوگوی Call Of Duty را در دو ردیف می‌سازد.
        """
        ids = COD_LOGO_CUSTOM_EMOJI_IDS[:]

        while len(ids) < 12:
            ids.append(0)

        for i in range(6):
            self.append_custom_emoji_by_id(COD_LOGO_FALLBACK_EMOJI, ids[i])

        self.append("\n")

        for i in range(6, 12):
            self.append_custom_emoji_by_id(COD_LOGO_FALLBACK_EMOJI, ids[i])


# ============================================================
# FINAL CAPTION
# ============================================================

def build_caption_no_trim(description_en: str, account_number: int) -> Tuple[str, List[object]]:
    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    b = CaptionBuilder()

    b.append_custom_emoji("🔻", "red_triangle")
    b.append(" Has a barcode to prevent abuse & fraud\n\n")

    b.append(f"{ACCOUNT_NUMBER_TAG}{account_number}\n\n")

    b.append("Status")
    b.append_custom_emoji("🟢", "green_circle")
    b.append("\n\n")

    b.append_custom_emoji("🔗", "link")
    b.append(f" | Synced on: {now_text}\n\n")

    b.append_custom_emoji("📤", "outbox")
    b.append("| Description:\n\n")

    if description_en.strip():
        b.append(description_en.strip())
        b.append("\n\n")

    b.append_cod_logo()
    b.append("\n\n")

    if QUOTE_HASHTAGS:
        b.append_blockquote(HASHTAGS)
    else:
        b.append(HASHTAGS)

    b.append("\n\n")

    if is_valid_url(COD_BUY_SELL_URL):
        b.append_text_link("COD BUY SELL", COD_BUY_SELL_URL)
    else:
        b.append("COD BUY SELL")

    b.append("\n\n")

    b.append_custom_emoji("💰", "money")
    b.append("| Account Price: ")
    b.append(ACCOUNT_PRICE_TEXT)
    b.append("\n\n")

    b.append_custom_emoji("💬", "chat")
    b.append("Group ")
    b.append_text_link(GROUP_USERNAME, GROUP_URL)
    b.append("\n\n")

    b.append_custom_emoji("👤", "person")
    b.append("MM ")
    b.append_text_link(MM_USERNAME, MM_URL)
    b.append(" ")
    b.append_custom_emoji("💳", "card")

    if int(CUSTOM_EMOJI_IDS.get("mm_badge", 0) or 0):
        b.append(" ")
        b.append_custom_emoji("💀", "mm_badge")

    b.append("\n\n")

    b.append_custom_emoji("📝", "memo")
    b.append_text_link("Terms Of Service", TERMS_URL)
    b.append("\n\n")

    b.append_custom_emoji("💬", "chat")
    b.append_text_link("Reviews", REVIEWS_URL)
    b.append("\n\n")

    b.append_custom_emoji("❓", "question")
    b.append_text_link("How does it work?", HOW_IT_WORKS_URL)
    b.append("\n\n")

    b.append_custom_emoji("🌐", "globe")
    b.append_text_link("Website", WEBSITE_URL)
    b.append("\n\n")

    b.append_custom_emoji("🤖", "robot")
    b.append_text_link("Ad Posting Bot", AD_POSTING_BOT_URL)
    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote("BUY NOW", BUY_NOW_URL)
    else:
        b.append_text_link("BUY NOW", BUY_NOW_URL)

    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote("SELL YOUR ACCOUNT", SELL_YOUR_ACCOUNT_URL)
    else:
        b.append_text_link("SELL YOUR ACCOUNT", SELL_YOUR_ACCOUNT_URL)

    return b.text, b.entities


def build_final_caption(description_en: str, account_number: int) -> Tuple[str, List[object]]:
    description_en = normalize_text(description_en)

    text, entities = build_caption_no_trim(description_en, account_number)

    if MAX_CAPTION_LENGTH <= 0:
        return text, entities

    if len(text) <= MAX_CAPTION_LENGTH:
        return text, entities

    ellipsis = "\n..."

    low = 0
    high = len(description_en)
    best_description = ""

    while low <= high:
        mid = (low + high) // 2
        candidate = description_en[:mid].rstrip()

        if candidate:
            candidate = candidate + ellipsis

        candidate_text, _ = build_caption_no_trim(candidate, account_number)

        if len(candidate_text) <= MAX_CAPTION_LENGTH:
            best_description = candidate
            low = mid + 1
        else:
            high = mid - 1

    return build_caption_no_trim(best_description, account_number)


# ============================================================
# MESSAGE / MEDIA HELPERS
# ============================================================

def message_has_video(message) -> bool:
    if not message:
        return False

    if getattr(message, "video", None):
        return True

    document = getattr(message, "document", None)
    if not document:
        return False

    mime_type = getattr(document, "mime_type", "") or ""
    return mime_type.startswith("video/")


def get_message_unique_key(message) -> str:
    chat_id = getattr(message, "chat_id", None) or "unknown"
    return f"{chat_id}:{message.id}"


def ensure_temp_dir() -> None:
    os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)


def safe_remove_file(path: Optional[str]) -> None:
    if not path:
        return

    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ============================================================
# TELEGRAM CLIENT
# ============================================================

if TELEGRAM_SESSION_STRING:
    client = TelegramClient(StringSession(TELEGRAM_SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

processed_ids = load_processed_ids()

# برای جلوگیری از تداخل شمارنده وقتی چند پست همزمان می‌آید
account_counter_lock = asyncio.Lock()


async def print_custom_emoji_ids_from_saved_messages(limit: int = 30) -> None:
    """
    از آخرین پیام‌های Saved Messages ایموجی‌های پرمیوم را پیدا می‌کند
    و document_id آن‌ها را چاپ می‌کند.
    """
    await client.start()

    messages = await client.get_messages("me", limit=limit)

    print("\nChecking Saved Messages for premium custom emojis...\n")

    found = False

    for msg in messages:
        if not msg.message or not msg.entities:
            continue

        for entity in msg.entities:
            if isinstance(entity, types.MessageEntityCustomEmoji):
                found = True
                emoji_text = substring_by_utf16(
                    msg.message,
                    entity.offset,
                    entity.length,
                )

                print("=" * 60)
                print(f"Emoji Text : {emoji_text}")
                print(f"Document ID: {entity.document_id}")
                print(f"Offset     : {entity.offset}")
                print(f"Length     : {entity.length}")

    if not found:
        print("هیچ Premium Custom Emoji در آخرین پیام‌های Saved Messages پیدا نشد.")
        print("یک پیام شامل ایموجی‌های پرمیوم داخل Saved Messages بفرست و دوباره اجرا کن.")

    print("\nDone.\n")


async def send_video_with_new_caption(message, final_caption: str, entities: List[object]) -> None:
    ensure_temp_dir()

    downloaded_path = None

    try:
        print("Downloading media...")
        downloaded_path = await client.download_media(message, file=TEMP_DOWNLOAD_DIR)

        if not downloaded_path:
            raise RuntimeError("Download failed. downloaded_path is empty.")

        print("Uploading to destination channel...")

        await client.send_file(
            entity=DEST_ENTITY,
            file=downloaded_path,
            caption=final_caption,
            formatting_entities=entities,
            supports_streaming=True,
            force_document=False,
        )

    finally:
        safe_remove_file(downloaded_path)


async def process_message(message) -> None:
    unique_key = get_message_unique_key(message)

    if unique_key in processed_ids:
        print(f"Already processed: {unique_key}")
        return

    if ONLY_VIDEO and not message_has_video(message):
        print(f"Skipped non-video message: {unique_key}")
        return

    source_caption = message.message or ""

    if not source_caption:
        print(f"Skipped message without caption: {unique_key}")
        return

    description = extract_description_from_source_caption(source_caption)

    print("\n" + "=" * 60)
    print(f"New source message: {unique_key}")
    print("- Extracted Description:")
    print(description if description else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description:
        print(f"Skipped because description is empty after filtering: {unique_key}")
        return

    description_en = translate_to_english(description)

    print("- Translated Description:")
    print(description_en if description_en else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description_en:
        print(f"Skipped because translated description is empty: {unique_key}")
        return

    try:
        async with account_counter_lock:
            if unique_key in processed_ids:
                print(f"Already processed inside lock: {unique_key}")
                return

            account_number = load_account_counter()
            final_caption, entities = build_final_caption(description_en, account_number)

            print("- Account Number:", account_number)
            print("- Final Caption Length:", len(final_caption))
            print("- Entities Count:", len(entities))

            await send_video_with_new_caption(message, final_caption, entities)

            processed_ids.add(unique_key)
            save_processed_ids(processed_ids)

            increment_account_counter(account_number)

            print(f"Posted successfully: {unique_key}")
            print(f"Account number used: {account_number}")
            print(f"Next account number: {account_number + 1}")

    except FloodWaitError as e:
        print(f"FloodWait: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds + 5)
        await process_message(message)

    except Exception as e:
        print(f"Error while processing {unique_key}: {e}")


@client.on(events.NewMessage(chats=SOURCE_ENTITY))
async def new_message_handler(event):
    await process_message(event.message)


async def main() -> None:
    if not API_ID:
        raise RuntimeError("API_ID را داخل کد یا Railway Variables وارد کن.")

    if not API_HASH or API_HASH == "PUT_YOUR_API_HASH_HERE":
        raise RuntimeError("API_HASH را داخل کد یا Railway Variables وارد کن.")

    if RUN_MODE == "EMOJI_IDS":
        await print_custom_emoji_ids_from_saved_messages()
        return

    if not SOURCE_ENTITY:
        raise RuntimeError("SOURCE_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    if not DEST_ENTITY:
        raise RuntimeError("DEST_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    await client.start()

    me = await client.get_me()

    print("\nTelegram client started.")
    print(f"Logged in as: {me.first_name} / ID: {me.id}")
    print(f"Source channel: {SOURCE_ENTITY}")
    print(f"Destination channel: {DEST_ENTITY}")
    print(f"Data dir: {DATA_DIR}")
    print(f"Counter file: {ACCOUNT_COUNTER_FILE}")
    print(f"Processed file: {PROCESSED_FILE}")
    print(f"Next account number: {load_account_counter()}")
    print("Listening for new video posts...\n")

    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())