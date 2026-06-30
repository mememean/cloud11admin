"""Mock BE API for the Happenings module.

Simulates the real App backend (Cloud11 Event & Ticket API + Creator Event & Ticket API).
Replace list_events()/get_event() with real HTTP calls when the BE endpoints are ready —
the response shape below is the contract the frontend (public/js/happenings-api.js) expects.
"""

EVENTS = [
    {
        "id": "collective-by-cloud11",
        "source": "cloud11",
        "title": "Collective by Cloud11",
        "venue": "Black Box Theater",
        "date_range": "10 Jun - 17 Jun 2024",
        "image": "/uploads/Header.webp",
        "description": "Cloud 11 — Creator Economy Hub ส่งเสริมคอมมูนิตี้สร้างสรรค์ และพื้นที่แลกเปลี่ยนไอเดียระหว่างครีเอเตอร์ในระบบนิเวศของ Cloud 11",
        "gallery": ["/uploads/Header.webp", "/uploads/Header_1.webp", "/uploads/Header_2.webp"],
        "tickets": [
            {"name": "Early Bird Ticket", "note": "Limit release pricing"},
            {"name": "Regular Ticket", "note": "Entry to festival ground"},
            {"name": "VIP Ticket", "note": "Premium access & perks"},
        ],
        "organizer": {"name": "ทินบุหงา นาวีพันธ์ (พิงค์)", "phone": "+6694-429-6361", "email": "film.kissayakorn@rabbitstale.com"},
    },
    {
        "id": "sound-design-masterclass",
        "source": "creator",
        "title": "Sound Design Masterclass with 1500 Sound Academy",
        "venue": "Black Box Theater",
        "date_range": "10 Jun - 17 Jun 2024",
        "image": "/uploads/Header_1.webp",
        "description": "เรียนรู้การออกแบบเสียงจากผู้เชี่ยวชาญตัวจริง ปูพื้นฐานสู่งานระดับมืดอาชีพ",
        "gallery": ["/uploads/Header_1.webp"],
        "tickets": [
            {"name": "Regular Ticket", "note": "Entry to workshop"},
        ],
        "organizer": {"name": "1500 Sound Academy", "phone": "+6694-000-0000", "email": "contact@1500sound.com"},
    },
    {
        "id": "photography-light-exhibition",
        "source": "creator",
        "title": "Photography & Light Exhibition Opening",
        "venue": "Black Box Theater",
        "date_range": "10 Jun - 17 Jun 2024",
        "image": "/uploads/Header_2.webp",
        "description": "นิทรรศการภาพถ่ายและแสง สำรวจมุมมองใหม่ของการเล่าเรื่องผ่านภาพ",
        "gallery": ["/uploads/Header_2.webp"],
        "tickets": [
            {"name": "Free Entry", "note": "Walk-in, limited capacity"},
        ],
        "organizer": {"name": "Cloud11 Bangkok", "phone": "+6694-111-2222", "email": "events@cloud11bangkok.com"},
    },
]


def list_events(source=None):
    if source in ("cloud11", "creator"):
        return [e for e in EVENTS if e["source"] == source]
    return EVENTS


def get_event(event_id):
    for e in EVENTS:
        if e["id"] == event_id:
            return e
    return None
