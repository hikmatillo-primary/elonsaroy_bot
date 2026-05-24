from dataclasses import dataclass

from app.models.ad import Category


@dataclass
class Question:
    key: str
    prompt: str
    options: list[tuple[str, str]] | None = None
    optional: bool = False
    is_title: bool = False
    is_price: bool = False
    field_type: str = "text"
    max_length: int = 500
    min_length: int = 1


CATEGORY_QUESTIONS: dict[Category, list[Question]] = {
    Category.AUTO: [
        Question(key="title", prompt="🚗 Avtomobil markasi va modelini kiriting:", is_title=True),
        Question(key="year", prompt="📅 Ishlab chiqarilgan yilini kiriting:", field_type="integer"),
        Question(key="mileage", prompt="🛣 Probegini kiriting (km):", field_type="integer"),
        Question(key="color", prompt="🎨 Rangini kiriting:", max_length=50),
        Question(
            key="condition", prompt="📊 Holatini tanlang:",
            options=[("new", "Yangi"), ("good", "Yaxshi"), ("average", "O'rtacha")],
        ),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.REALESTATE: [
        Question(key="title", prompt="🏠 Uy-joy turini kiriting (masalan: 3 xonali kvartira):", is_title=True),
        Question(key="rooms", prompt="🚪 Xonalar sonini kiriting:", field_type="integer"),
        Question(key="area", prompt="📐 Umumiy maydonni kiriting (m²):", field_type="number"),
        Question(key="address", prompt="📍 Manzilni kiriting:", min_length=3, max_length=200),
        Question(key="floor", prompt="🏢 Qavatni kiriting:", field_type="integer"),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.PHONE: [
        Question(key="title", prompt="📱 Telefon modelini kiriting:", is_title=True),
        Question(key="storage", prompt="💾 Xotira hajmini kiriting (masalan: 128 GB):"),
        Question(
            key="condition", prompt="📊 Holatini tanlang:",
            options=[("new", "Yangi"), ("good", "Yaxshi"), ("average", "O'rtacha")],
        ),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.JOBS: [
        Question(key="title", prompt="💼 Lavozim nomini kiriting:", is_title=True),
        Question(key="company", prompt="🏢 Tashkilot/kompaniya nomini kiriting:", min_length=2, max_length=100),
        Question(
            key="job_type", prompt="⏰ Ish turini tanlang:",
            options=[("full_time", "To'liq stavka"), ("part_time", "Yarim stavka"), ("remote", "Masofaviy")],
        ),
        Question(key="requirements", prompt="📋 Talablarni kiriting:"),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="salary", prompt="💰 Maosh miqdorini kiriting:", is_price=True, optional=True),
    ],
}


def validate_answer(question: Question, text: str) -> str | None:
    text = text.strip()
    if not text:
        return "Bo'sh javob kiritish mumkin emas."
    if question.field_type == "integer":
        if not text.isdigit():
            return "Iltimos, butun son kiriting (masalan: 2020)."
    elif question.field_type == "number":
        try:
            float(text.replace(",", "."))
        except ValueError:
            return "Iltimos, son kiriting (masalan: 65.5)."
    if len(text) < question.min_length:
        return f"Kamida {question.min_length} belgi kiriting."
    if len(text) > question.max_length:
        return f"Maksimal {question.max_length} belgi kiritish mumkin."
    return None


DESCRIPTION_FIELDS: dict[Category, list[tuple[str, str]]] = {
    Category.AUTO: [
        ("year", "📅 Yili"),
        ("mileage", "🛣 Probeg"),
        ("color", "🎨 Rang"),
        ("condition", "📊 Holati"),
        ("extra", ""),
    ],
    Category.REALESTATE: [
        ("rooms", "🚪 Xonalar"),
        ("area", "📐 Maydon"),
        ("address", "📍 Manzil"),
        ("floor", "🏢 Qavat"),
        ("extra", ""),
    ],
    Category.PHONE: [
        ("storage", "💾 Xotira"),
        ("condition", "📊 Holati"),
        ("extra", ""),
    ],
    Category.JOBS: [
        ("company", "🏢 Kompaniya"),
        ("job_type", "⏰ Ish turi"),
        ("requirements", "📋 Talablar"),
        ("extra", ""),
    ],
}


def build_description(category: Category, answers: dict[str, str]) -> str:
    fields = DESCRIPTION_FIELDS.get(category, [])
    lines = []
    for key, label in fields:
        value = answers.get(key)
        if value:
            if label:
                lines.append(f"{label}: {value}")
            else:
                lines.append(value)
    return "\n".join(lines)


def get_price_from_answers(category: Category, answers: dict[str, str]) -> str | None:
    questions = CATEGORY_QUESTIONS[category]
    for q in questions:
        if q.is_price:
            return answers.get(q.key) or None
    return None


def get_title_from_answers(category: Category, answers: dict[str, str]) -> str:
    questions = CATEGORY_QUESTIONS[category]
    for q in questions:
        if q.is_title:
            return answers.get(q.key, "")
    return ""
