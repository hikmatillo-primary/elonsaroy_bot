from dataclasses import dataclass

from app.models.ad import Category


@dataclass
class Question:
    key: str
    prompt: str
    options: list[str] | None = None
    optional: bool = False
    is_title: bool = False
    is_price: bool = False


CATEGORY_QUESTIONS: dict[Category, list[Question]] = {
    Category.AUTO: [
        Question(key="title", prompt="🚗 Avtomobil markasi va modelini kiriting:", is_title=True),
        Question(key="year", prompt="📅 Ishlab chiqarilgan yilini kiriting:"),
        Question(key="mileage", prompt="🛣 Probegini kiriting (km):"),
        Question(key="color", prompt="🎨 Rangini kiriting:"),
        Question(key="condition", prompt="📊 Holatini tanlang:", options=["Yangi", "Yaxshi", "O'rtacha"]),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.REALESTATE: [
        Question(key="title", prompt="🏠 Uy-joy turini kiriting (masalan: 3 xonali kvartira):", is_title=True),
        Question(key="rooms", prompt="🚪 Xonalar sonini kiriting:"),
        Question(key="area", prompt="📐 Umumiy maydonni kiriting (m²):"),
        Question(key="address", prompt="📍 Manzilni kiriting:"),
        Question(key="floor", prompt="🏢 Qavatni kiriting:"),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.PHONE: [
        Question(key="title", prompt="📱 Telefon modelini kiriting:", is_title=True),
        Question(key="storage", prompt="💾 Xotira hajmini kiriting (masalan: 128 GB):"),
        Question(key="condition", prompt="📊 Holatini tanlang:", options=["Yangi", "Yaxshi", "O'rtacha"]),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="price", prompt="💰 Narxini kiriting:", is_price=True, optional=True),
    ],
    Category.JOBS: [
        Question(key="title", prompt="💼 Lavozim nomini kiriting:", is_title=True),
        Question(key="company", prompt="🏢 Tashkilot/kompaniya nomini kiriting:"),
        Question(key="job_type", prompt="⏰ Ish turini tanlang:", options=["To'liq stavka", "Yarim stavka", "Masofaviy"]),
        Question(key="requirements", prompt="📋 Talablarni kiriting:"),
        Question(key="extra", prompt="📝 Qo'shimcha ma'lumot kiriting:", optional=True),
        Question(key="salary", prompt="💰 Maosh miqdorini kiriting:", is_price=True, optional=True),
    ],
}


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
