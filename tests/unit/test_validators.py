from datetime import date

import pytest

from app.validators import (
    ValidationFailed,
    validate_email,
    validate_movie,
    validate_password,
    validate_report,
)

TODAY = date(2025, 6, 1)


def test_email_is_normalized():
    assert validate_email("  User@Example.COM ") == "user@example.com"


@pytest.mark.parametrize("bad", ["", "no-at-sign", "a@b", "a b@c.com", "@x.com"])
def test_invalid_email_rejected(bad):
    with pytest.raises(ValidationFailed):
        validate_email(bad)


def test_short_password_rejected():
    with pytest.raises(ValidationFailed):
        validate_password("short")


def test_movie_title_is_trimmed():
    assert validate_movie("  Dune  ", " Sci-Fi ", 100) == ("Dune", "Sci-Fi")


@pytest.mark.parametrize("title,genre,budget", [("", "Drama", 1), ("X", " ", 1), ("X", "Drama", 0)])
def test_invalid_movie_rejected(title, genre, budget):
    with pytest.raises(ValidationFailed):
        validate_movie(title, genre, budget)


def test_report_valid_returns_uppercase_region():
    region = validate_report(date(2025, 5, 1), date(2025, 4, 1), "us", 10, 1, today=TODAY)
    assert region == "US"


def test_report_in_future_rejected():
    with pytest.raises(ValidationFailed):
        validate_report(date(2025, 7, 1), date(2025, 4, 1), "US", 10, 1, today=TODAY)


def test_report_before_release_rejected():
    with pytest.raises(ValidationFailed):
        validate_report(date(2025, 3, 1), date(2025, 4, 1), "US", 10, 1, today=TODAY)


@pytest.mark.parametrize("region", ["", "USA", "1A", "U"])
def test_bad_region_rejected(region):
    with pytest.raises(ValidationFailed):
        validate_report(date(2025, 5, 1), date(2025, 4, 1), region, 10, 1, today=TODAY)


@pytest.mark.parametrize("revenue,tickets", [(-1, 0), (0, -1)])
def test_negative_amounts_rejected(revenue, tickets):
    with pytest.raises(ValidationFailed):
        validate_report(date(2025, 5, 1), date(2025, 4, 1), "US", revenue, tickets, today=TODAY)
