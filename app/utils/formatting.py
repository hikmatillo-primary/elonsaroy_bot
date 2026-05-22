from app.models.ad import Ad, CATEGORY_LABELS


def format_ad_text(ad: Ad, include_contact: bool = True) -> str:
    lines = [
        f"<b>{CATEGORY_LABELS.get(ad.category, ad.category.value)}</b>",
        "",
        f"<b>{ad.title}</b>",
        "",
        ad.description,
    ]
    if ad.price:
        lines.append(f"\n💰 <b>Narx:</b> {ad.price}")
    if include_contact:
        lines.append(f"\n📞 <b>Aloqa:</b> {ad.contact_phone}")
    return "\n".join(lines)
