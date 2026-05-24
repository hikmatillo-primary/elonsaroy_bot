import pytest

from app.handlers.question_flow import (
    CATEGORY_QUESTIONS,
    Question,
    build_description,
    get_price_from_answers,
    get_title_from_answers,
    validate_answer,
)
from app.models.ad import Category


class TestQuestionFlow:
    def test_all_categories_have_questions(self):
        for cat in Category:
            assert cat in CATEGORY_QUESTIONS
            assert len(CATEGORY_QUESTIONS[cat]) > 0

    def test_each_category_has_title_question(self):
        for cat in Category:
            title_qs = [q for q in CATEGORY_QUESTIONS[cat] if q.is_title]
            assert len(title_qs) == 1

    def test_each_category_has_price_question(self):
        for cat in Category:
            price_qs = [q for q in CATEGORY_QUESTIONS[cat] if q.is_price]
            assert len(price_qs) == 1

    def test_build_description_auto(self):
        answers = {
            "title": "Chevrolet Malibu",
            "year": "2020",
            "mileage": "50000",
            "color": "Oq",
            "condition": "Yaxshi",
            "extra": "Ideal holat",
        }
        desc = build_description(Category.AUTO, answers)
        assert "2020" in desc
        assert "50000" in desc
        assert "Oq" in desc
        assert "Yaxshi" in desc
        assert "Ideal holat" in desc

    def test_build_description_realestate(self):
        answers = {
            "title": "3 xonali kvartira",
            "rooms": "3",
            "area": "85",
            "address": "Toshkent, Yunusobod",
            "floor": "5",
        }
        desc = build_description(Category.REALESTATE, answers)
        assert "3" in desc
        assert "85" in desc
        assert "Toshkent" in desc
        assert "5" in desc

    def test_build_description_phone(self):
        answers = {
            "title": "iPhone 15 Pro",
            "storage": "256 GB",
            "condition": "Yangi",
        }
        desc = build_description(Category.PHONE, answers)
        assert "256 GB" in desc
        assert "Yangi" in desc

    def test_build_description_jobs(self):
        answers = {
            "title": "Python Developer",
            "company": "IT Company",
            "job_type": "To'liq stavka",
            "requirements": "3 yil tajriba",
        }
        desc = build_description(Category.JOBS, answers)
        assert "IT Company" in desc
        assert "To'liq stavka" in desc
        assert "3 yil tajriba" in desc

    def test_build_description_skips_empty_fields(self):
        answers = {"title": "Test", "year": "2020"}
        desc = build_description(Category.AUTO, answers)
        assert "2020" in desc
        assert "Rang" not in desc

    def test_get_price_from_answers_auto(self):
        answers = {"price": "15000 USD"}
        assert get_price_from_answers(Category.AUTO, answers) == "15000 USD"

    def test_get_price_from_answers_jobs_salary(self):
        answers = {"salary": "5 mln so'm"}
        assert get_price_from_answers(Category.JOBS, answers) == "5 mln so'm"

    def test_get_price_from_answers_empty(self):
        answers = {}
        assert get_price_from_answers(Category.AUTO, answers) is None

    def test_get_title_from_answers(self):
        answers = {"title": "Test Title"}
        assert get_title_from_answers(Category.AUTO, answers) == "Test Title"

    def test_get_title_from_answers_empty(self):
        answers = {}
        assert get_title_from_answers(Category.AUTO, answers) == ""

    def test_optional_questions_marked_correctly(self):
        for cat in Category:
            for q in CATEGORY_QUESTIONS[cat]:
                if q.key in ("extra",):
                    assert q.optional, f"{cat.value}.{q.key} should be optional"
                if q.is_price:
                    assert q.optional, f"{cat.value} price question should be optional"

    def test_options_are_tuples(self):
        for cat in Category:
            for q in CATEGORY_QUESTIONS[cat]:
                if q.options:
                    for opt in q.options:
                        assert isinstance(opt, tuple) and len(opt) == 2


class TestValidateAnswer:
    def test_integer_field_rejects_text(self):
        q = Question(key="year", prompt="Year:", field_type="integer")
        assert validate_answer(q, "abc") is not None

    def test_integer_field_accepts_digits(self):
        q = Question(key="year", prompt="Year:", field_type="integer")
        assert validate_answer(q, "2020") is None

    def test_number_field_rejects_text(self):
        q = Question(key="area", prompt="Area:", field_type="number")
        assert validate_answer(q, "big") is not None

    def test_number_field_accepts_float(self):
        q = Question(key="area", prompt="Area:", field_type="number")
        assert validate_answer(q, "65.5") is None

    def test_number_field_accepts_comma_decimal(self):
        q = Question(key="area", prompt="Area:", field_type="number")
        assert validate_answer(q, "65,5") is None

    def test_min_length_check(self):
        q = Question(key="address", prompt="Address:", min_length=3)
        assert validate_answer(q, "ab") is not None

    def test_max_length_check(self):
        q = Question(key="color", prompt="Color:", max_length=50)
        assert validate_answer(q, "x" * 51) is not None

    def test_empty_string_rejected(self):
        q = Question(key="title", prompt="Title:")
        assert validate_answer(q, "   ") is not None

    def test_valid_text_accepted(self):
        q = Question(key="title", prompt="Title:")
        assert validate_answer(q, "Chevrolet Malibu") is None
