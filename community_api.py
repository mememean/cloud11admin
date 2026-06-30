"""Mock BE API for the Your Space / Community Space carousel.

Simulates the real App backend (Community Booking System). Replace list_spaces()/get_space()
with real HTTP calls when the BE endpoint is ready — the response shape below is the contract
the admin's read-only EventSourceTable-pattern table (Community Space) expects.
"""

SPACES = [
    {
        "id": "studio-a-hall",
        "source": "booking_system",
        "title": "Studio A — Event Hall",
        "subtitle": "Up to 200 pax, full AV setup",
        "image": "/uploads/Header.webp",
        "description": "Flexible event hall for talks, launches, and community gatherings — full AV, stage, and breakout space.",
        "capacity": "200 pax",
        "hours": "08:00 – 22:00 daily",
    },
    {
        "id": "rooftop-court",
        "source": "booking_system",
        "title": "Rooftop Sports Court",
        "subtitle": "Multi-purpose outdoor court",
        "image": "/uploads/Header_1.webp",
        "description": "Open-air multi-purpose court for basketball, futsal, and community sport sessions.",
        "capacity": "30 pax",
        "hours": "06:00 – 21:00 daily",
    },
    {
        "id": "maker-studio",
        "source": "booking_system",
        "title": "Maker Studio",
        "subtitle": "Bookable creator workspace",
        "image": "/uploads/Header_2.webp",
        "description": "Hands-on workspace with tools and bench space for makers, designers, and small-batch production.",
        "capacity": "15 pax",
        "hours": "09:00 – 20:00 daily",
    },
]


def list_spaces():
    return SPACES


def get_space(space_id):
    for s in SPACES:
        if s["id"] == space_id:
            return s
    return None
