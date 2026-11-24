import re
from datetime import date

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REGION_RE = re.compile(r"^[A-Za-z]{2}$")


class ValidationFailed(ValueError):
    pass


def validate_email(email: str) -> str:
    email = (email or "").strip().lower()
    if len(email) > 254 or not EMAIL_RE.match(email):
        raise ValidationFailed("Invalid email address")
    return email


def validate_password(password: str) -> None:
    if len(password or "") < 8:
        raise ValidationFailed("Password must be at least 8 characters long")


def validate_movie(title: str, genre: str, budget_usd: int) -> tuple[str, str]:
    title = (title or "").strip()
    genre = (genre or "").strip()
    if not title or len(title) > 200:
        raise ValidationFailed("Title must be 1..200 characters")
    if not genre or len(genre) > 50:
        raise ValidationFailed("Genre must be 1..50 characters")
    if budget_usd <= 0:
        raise ValidationFailed("Budget must be greater than zero")
    return title, genre


def validate_amounts(revenue_usd: int, tickets_sold: int) -> None:
    if revenue_usd < 0:
        raise ValidationFailed("Revenue cannot be negative")
    if tickets_sold < 0:
        raise ValidationFailed("Tickets sold cannot be negative")


def validate_report(
    report_date: date,
    release_date: date,
    region: str,
    revenue_usd: int,
    tickets_sold: int,
    today: date | None = None,
) -> str:
    today = today or date.today()
    if report_date > today:
        raise ValidationFailed("Report date cannot be in the future")
    if report_date < release_date:
        raise ValidationFailed("Report date cannot be earlier than the movie release date")
    if not REGION_RE.match(region or ""):
        raise ValidationFailed("Region must be a 2-letter code, e.g. US")
    validate_amounts(revenue_usd, tickets_sold)
    return region.upper()
