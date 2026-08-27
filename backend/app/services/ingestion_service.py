import hashlib
import re
import html
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.models.sources import (
    Source, SourceDocument, IngestionRun, IngestionItem, SourceAuthorityLevel, IngestionRunStatus
)
from app.models.news import (
    NewsArticle, NewsTranslation, NewsVersion, NewsSource, NewsCategory, NewsStatus
)
from app.models.localization import LocalizationGlossary
from app.services.glossary_service import KazakhLanguageQAService


class IngestionSecurityError(Exception):
    pass


class IngestionEngine:
    """
    Production-grade, idempotent knowledge ingestion engine.
    Treats external content strictly as passive data with active prompt injection defenses.
    """

    ALLOWED_SCHEMES = {"http", "https"}
    ALLOWED_DOMAINS = {
        "testcenter.kz",
        "www.testcenter.kz",
        "gov.kz",
        "www.gov.kz",
        "edu.gov.kz",
        "www.edu.gov.kz",
        "bilimdinews.kz",
        "daryn.kz",
        "nis.edu.kz",
    }

    UNT_RELEVANCE_KEYWORDS = {
        "ұбт": 0.35,
        "ент": 0.35,
        "тестілеу": 0.20,
        "тестирование": 0.20,
        "информатика": 0.30,
        "грант": 0.25,
        "талапкер": 0.20,
        "абитуриент": 0.20,
        "шекті балл": 0.25,
        "проходной балл": 0.25,
        "бейіндік пән": 0.20,
        "профильный предмет": 0.20,
        "тіркелу": 0.15,
        "регистрация": 0.15,
        "ұлттық бірыңғай тестілеу": 0.40,
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.qa_service = KazakhLanguageQAService(session)

    def sanitize_external_text(self, text: str) -> str:
        """
        Removes HTML tags, dangerous escape sequences, and neutralizes prompt-injection triggers.
        """
        if not text:
            return ""
        # 1. Unescape HTML entities
        clean = html.unescape(text)
        # 2. Strip all HTML tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # 3. Strip excessive whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        # 4. Prompt injection defense: neutralize common override directives
        injection_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"you\s+are\s+now\s+in\s+developer\s+mode",
            r"system\s*prompt\s*override",
        ]
        for pat in injection_patterns:
            clean = re.sub(pat, "[FILTERED_SECURITY_DIRECTIVE]", clean, flags=re.IGNORECASE)
        return clean

    def compute_content_hash(self, text: str) -> str:
        """
        Computes deterministic SHA-256 hash of normalized text for exact deduplication.
        """
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def validate_url(self, url: str) -> bool:
        """
        SSRF defense: validates protocol scheme and domain whitelist.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in self.ALLOWED_SCHEMES:
                return False
            hostname = parsed.hostname.lower() if parsed.hostname else ""
            return any(hostname == domain or hostname.endswith("." + domain) for domain in self.ALLOWED_DOMAINS)
        except Exception:
            return False

    def calculate_relevance(self, title: str, content: str) -> Tuple[float, str]:
        """
        Calculates UNT relevance score (0.00 to 1.00) and infers the primary category.
        """
        combined = (title + " " + content).lower()
        score = 0.0
        for kw, weight in self.UNT_RELEVANCE_KEYWORDS.items():
            if kw in combined:
                score += weight

        relevance = min(1.0, round(score, 2))

        # Categorize
        if "информатика" in combined:
            category = NewsCategory.INFORMATICS
        elif "грант" in combined:
            category = NewsCategory.GRANTS
        elif "тіркелу" in combined or "регистрация" in combined or "мерзім" in combined or "дедлайн" in combined:
            category = NewsCategory.REGISTRATION
        elif "нәтиже" in combined or "результат" in combined:
            category = NewsCategory.EXAM_RESULTS
        elif "ереже" in combined or "спецификация" in combined or "құрылым" in combined:
            category = NewsCategory.SPECIFICATION
        else:
            category = NewsCategory.UNT

        return relevance, category

    async def ingest_news_item(
        self,
        run_id: int,
        source: Source,
        canonical_url: str,
        title_kk: str,
        summary_kk: str,
        content_kk: str,
        title_ru: Optional[str] = None,
        summary_ru: Optional[str] = None,
        content_ru: Optional[str] = None,
        title_en: Optional[str] = None,
        summary_en: Optional[str] = None,
        content_en: Optional[str] = None,
        published_at: Optional[datetime] = None,
        is_breaking: bool = False,
        importance_score: int = 5,
    ) -> Dict[str, Any]:
        """
        Processes a single news item idempotently:
        - Validates URL
        - Sanitizes text
        - Computes content hash
        - Checks for exact or existing canonical URL
        - If updated: updates translations & logs version
        - If new: creates NewsArticle, NewsTranslations, and IngestionItem record
        """
        if not self.validate_url(canonical_url):
            raise IngestionSecurityError(f"URL validation failed for: {canonical_url}")

        clean_title_kk = self.sanitize_external_text(title_kk)
        clean_summary_kk = self.sanitize_external_text(summary_kk)
        clean_content_kk = self.sanitize_external_text(content_kk)
        content_hash = self.compute_content_hash(clean_title_kk + " " + clean_content_kk)

        if not published_at:
            published_at = datetime.now(timezone.utc)

        relevance, category = self.calculate_relevance(clean_title_kk, clean_content_kk)

        # Check existing article by canonical URL with eager loaded relationships
        existing_res = await self.session.execute(
            select(NewsArticle)
            .options(selectinload(NewsArticle.versions), selectinload(NewsArticle.translations))
            .where(NewsArticle.canonical_url == canonical_url)
        )
        existing_article = existing_res.scalars().first()

        action = "skipped"

        if existing_article:
            # Check if content has changed
            if existing_article.content_hash != content_hash:
                # Content changed at source! Record version and update
                new_version = NewsVersion(
                    news_id=existing_article.id,
                    version_number=len(existing_article.versions) + 1,
                    title=clean_title_kk,
                    content=clean_content_kk,
                    content_hash=content_hash,
                    change_summary="Official source updated content",
                )
                self.session.add(new_version)

                existing_article.content_hash = content_hash
                existing_article.last_verified_at = datetime.now(timezone.utc)
                existing_article.relevance_score = relevance
                existing_article.category = category

                # Update translations
                # (Kazakh)
                await self._upsert_translation(existing_article.id, "kk", clean_title_kk, clean_summary_kk, clean_content_kk)
                if title_ru:
                    await self._upsert_translation(existing_article.id, "ru", self.sanitize_external_text(title_ru), self.sanitize_external_text(summary_ru or ""), self.sanitize_external_text(content_ru or ""))
                if title_en:
                    await self._upsert_translation(existing_article.id, "en", self.sanitize_external_text(title_en), self.sanitize_external_text(summary_en or ""), self.sanitize_external_text(content_en or ""))

                action = "updated"
            else:
                # Same content, touch freshness timestamp
                existing_article.last_verified_at = datetime.now(timezone.utc)
                action = "skipped"

            article_id = existing_article.id
        else:
            # Create brand new article
            article = NewsArticle(
                canonical_url=canonical_url,
                source_id=source.id,
                category=category,
                original_language=source.default_language,
                importance_score=importance_score,
                relevance_score=relevance,
                is_breaking=is_breaking,
                status=NewsStatus.PUBLISHED if (relevance >= 0.25 and source.authority_level.startswith("official")) else NewsStatus.PENDING_REVIEW,
                content_hash=content_hash,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc),
                last_verified_at=datetime.now(timezone.utc),
            )
            self.session.add(article)
            await self.session.flush()

            article_id = article.id

            # Add translations
            await self._upsert_translation(article_id, "kk", clean_title_kk, clean_summary_kk, clean_content_kk)
            if title_ru:
                await self._upsert_translation(article_id, "ru", self.sanitize_external_text(title_ru), self.sanitize_external_text(summary_ru or ""), self.sanitize_external_text(content_ru or ""))
            if title_en:
                await self._upsert_translation(article_id, "en", self.sanitize_external_text(title_en), self.sanitize_external_text(summary_en or ""), self.sanitize_external_text(content_en or ""))

            # Record provenance
            news_source = NewsSource(
                news_id=article_id,
                source_id=source.id,
                external_url=canonical_url,
                attribution_text=f"{source.name} ({source.authority_level})"
            )
            self.session.add(news_source)

            action = "created"

        # Log item to IngestionItem for full observability
        item_log = IngestionItem(
            run_id=run_id,
            item_type="news",
            external_identifier=canonical_url,
            content_hash=content_hash,
            action_taken=action,
        )
        self.session.add(item_log)
        await self.session.flush()

        return {
            "article_id": article_id,
            "action": action,
            "relevance": relevance,
            "category": category,
        }

    async def _upsert_translation(self, news_id: int, locale: str, title: str, summary: str, content: str):
        existing_res = await self.session.execute(
            select(NewsTranslation).where(
                NewsTranslation.news_id == news_id,
                NewsTranslation.locale == locale
            )
        )
        trans = existing_res.scalars().first()
        if trans:
            trans.title = title
            trans.summary = summary
            trans.content = content
        else:
            trans = NewsTranslation(
                news_id=news_id,
                locale=locale,
                title=title,
                summary=summary,
                content=content,
                translation_source="official" if locale == "kk" else "human",
                translation_status="published",
            )
            self.session.add(trans)
        await self.session.flush()
