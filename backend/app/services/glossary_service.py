import re
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.localization import LocalizationGlossary


class KazakhLanguageQAService:
    """
    Validates Kazakh language quality, checks for typical mechanical translation errors,
    and enforces official Kazakhstan educational and IT terminology.
    """

    # Common machine-translation blunders to detect and flag
    CALQUE_PATTERNS = [
        (r"\bбаза данных\b", "Деректер базасы (немесе дерекқор) қолданылуы тиіс"),
        (r"\bисходный код\b", "Бастапқы код қолданылуы тиіс"),
        (r"\bучетная запись\b", "Тіркелгі қолданылуы тиіс"),
        (r"\bпо умолчанию\b", "Әдепкі бойынша (немесе үнсіз келісім бойынша) қолданылуы тиіс"),
        (r"\bтестирование өткізу\b", "Тестілеу жүргізу қолданылуы тиіс"),
        (r"\bбалл жинау\b", "Балл жинақтау қолданылуы тиіс"),
    ]

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all_glossary_terms(self) -> List[LocalizationGlossary]:
        if not self.session:
            return []
        result = await self.session.execute(
            select(LocalizationGlossary).where(LocalizationGlossary.approved == True)
        )
        return list(result.scalars().all())

    def validate_kazakh_text(self, text: str) -> Dict[str, any]:
        """
        Runs quality checks on a Kazakh text string.
        Returns validation result: is_valid, warnings, suggestions.
        """
        if not text or not text.strip():
            return {"is_valid": False, "score": 0.0, "warnings": ["Мәтін бос"]}

        warnings = []
        
        # 1. Check for untranslated Cyrillic Russian tokens in Kazakh text
        russian_only_chars = set("ыэъё")
        has_russian_specific = any(char in text.lower() for char in "ъ")
        if has_russian_specific:
            warnings.append("Қазақ мәтінінде 'ъ' таңбасы кездесті")

        # 2. Check calque / non-standard phrases
        for pattern, recommendation in self.CALQUE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(f"Сөздік қатесі: {recommendation}")

        # 3. Check for typical Kazakh specific letters presence in long text
        kazakh_specific_chars = set("әіңғүұқөһ")
        has_kazakh_specific = any(char in text.lower() for char in kazakh_specific_chars)
        
        # In a paragraph of more than 100 chars, absence of any Kazakh letters might indicate untranslated Russian
        if len(text) > 120 and not has_kazakh_specific:
            warnings.append("Мәтінде қазақ әріптері (ә, і, ң, ғ, ү, ұ, қ, ө, һ) табылмады, орыс тіліндегі мәтін болуы мүмкін")

        is_valid = len([w for w in warnings if "болуы мүмкін" in w or "таңбасы" in w]) == 0
        quality_score = max(0.0, 1.0 - (len(warnings) * 0.2))

        return {
            "is_valid": is_valid,
            "quality_score": round(quality_score, 2),
            "warnings": warnings,
        }

    def apply_glossary_substitutions(self, text: str, glossary_dict: Dict[str, str]) -> str:
        """
        Substitutes terminology keywords based on verified glossary mapping.
        """
        output = text
        for term, official_term in glossary_dict.items():
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            output = pattern.sub(official_term, output)
        return output
