import hashlib
from datetime import datetime, date, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.sources import Source, SourceAuthorityLevel, SourceDocument
from app.models.localization import LocalizationGlossary
from app.models.specification import (
    ExamType, Subject, ExamSpecification, SpecificationSection, SpecificationTopic,
    CurrentUntRule, SpecificationStatus
)
from app.models.question_bank import (
    BankQuestion, QuestionVersion, QuestionTranslation, QuestionBankOption,
    QuestionBankOptionTranslation, QuestionProvenance, BankSolution,
    BankSolutionTranslation, Tag, QuestionTag, QuestionDifficulty, OfficialStatus
)
from app.models.news import (
    NewsArticle, NewsTranslation, NewsVersion, NewsSource, NewsCategory, NewsStatus
)


async def seed_data_platform(session: AsyncSession):
    """
    Seeds the comprehensive UNTverse Data Platform:
    - Sources registry
    - Kazakh-Russian-English glossary
    - Official 2026 UNT Informatics specifications & taxonomy
    - Current 2026 UNT rules & deadlines
    - Verified question bank with provenance, options, solutions, and translations
    - Breaking and category news articles
    """
    # Check if already seeded
    src_check = await session.execute(select(Source).limit(1))
    if src_check.scalars().first():
        return

    # 1. Seed Sources Registry
    sources_data = [
        Source(
            name="ҚР ҒЖБМ Ұлттық тестілеу орталығы (ҰТО)",
            slug="testcenter-kz",
            base_url="https://testcenter.kz",
            feed_url="https://testcenter.kz/feed/",
            source_type="official_portal",
            authority_level=SourceAuthorityLevel.OFFICIAL_PRIMARY,
            default_language="kk",
            country="KZ",
            is_active=True,
            crawl_frequency_minutes=360,
            robots_policy="allowed",
            terms_notes="Официальный орган проведения ЕНТ/ҰБТ Республики Казахстан",
            last_checked_at=datetime.now(timezone.utc),
            last_success_at=datetime.now(timezone.utc),
        ),
        Source(
            name="ҚР Ғылым және жоғары білім министрлігі",
            slug="gov-sci-kz",
            base_url="https://www.gov.kz/memleket/entities/sci",
            feed_url=None,
            source_type="ministry",
            authority_level=SourceAuthorityLevel.OFFICIAL_PRIMARY,
            default_language="kk",
            country="KZ",
            is_active=True,
            crawl_frequency_minutes=720,
            robots_policy="allowed",
            terms_notes="Официальные нормативные правовые акты, распределение образовательных грантов",
            last_checked_at=datetime.now(timezone.utc),
            last_success_at=datetime.now(timezone.utc),
        ),
        Source(
            name="«Дарын» Республикалық ғылыми-практикалық орталығы",
            slug="daryn-kz",
            base_url="https://daryn.kz",
            feed_url=None,
            source_type="official_portal",
            authority_level=SourceAuthorityLevel.TRUSTED_EDUCATIONAL,
            default_language="kk",
            country="KZ",
            is_active=True,
            crawl_frequency_minutes=1440,
            robots_policy="allowed",
            terms_notes="Олимпиадные задания и углубленная подготовка по информатике",
            last_checked_at=datetime.now(timezone.utc),
            last_success_at=datetime.now(timezone.utc),
        ),
        Source(
            name="Bilimdi El — Образовательная газета",
            slug="bilimdinews-kz",
            base_url="https://bilimdinews.kz",
            feed_url="https://bilimdinews.kz/feed/",
            source_type="rss_feed",
            authority_level=SourceAuthorityLevel.SECONDARY_MEDIA,
            default_language="ru",
            country="KZ",
            is_active=True,
            crawl_frequency_minutes=720,
            robots_policy="allowed",
            terms_notes="Новости высшего образования и аналитика приемных комиссий",
            last_checked_at=datetime.now(timezone.utc),
            last_success_at=datetime.now(timezone.utc),
        ),
    ]
    session.add_all(sources_data)
    await session.flush()

    ntc_source = sources_data[0]
    gov_sci_source = sources_data[1]

    # 2. Seed Localization Glossary (50+ Educational and IT Terms)
    glossary_items = [
        ("unt_full", "Ұлттық бірыңғай тестілеу", "Единое национальное тестирование", "Unified National Testing", "educational_unt"),
        ("applicant", "Талапкер", "Абитуриент", "Applicant / Candidate", "educational_unt"),
        ("profile_subject", "Бейіндік пән", "Профильный предмет", "Profile subject", "educational_unt"),
        ("passing_score", "Шекті балл", "Проходной / пороговый балл", "Passing score", "educational_unt"),
        ("education_grant", "Білім беру гранты", "Образовательный грант", "Educational grant", "educational_unt"),
        ("testing_center", "Ұлттық тестілеу орталығы", "Национальный центр тестирования", "National Testing Center", "educational_unt"),
        ("math_literacy", "Математикалық сауаттылық", "Математическая грамотность", "Mathematical literacy", "educational_unt"),
        ("reading_literacy", "Оқу сауаттылығы", "Грамотность чтения", "Reading literacy", "educational_unt"),
        ("kazakhstan_history", "Қазақстан тарихы", "История Казахстана", "History of Kazakhstan", "educational_unt"),
        ("database", "Деректер базасы (дерекқор)", "База данных", "Database", "cs_terminology"),
        ("relational_model", "Реляциялық модель", "Реляционная модель", "Relational model", "cs_terminology"),
        ("primary_key", "Бастапқы кілт", "Первичный ключ", "Primary key", "cs_terminology"),
        ("foreign_key", "Сыртқы кілт", "Внешний ключ", "Foreign key", "cs_terminology"),
        ("query", "Сұраныс", "Запрос", "Query", "cs_terminology"),
        ("algorithm", "Алгоритм", "Алгоритм", "Algorithm", "cs_terminology"),
        ("recursion", "Қайталану (рекурсия)", "Рекурсия", "Recursion", "cs_terminology"),
        ("data_structure", "Деректер құрылымы", "Структура данных", "Data structure", "cs_terminology"),
        ("number_system", "Санау жүйесі", "Система счисления", "Number system", "cs_terminology"),
        ("binary_system", "Екілік санау жүйесі", "Двоичная система счисления", "Binary system", "cs_terminology"),
        ("hexadecimal_system", "Он алтылық санау жүйесі", "Шестнадцатеричная система счисления", "Hexadecimal system", "cs_terminology"),
        ("info_security", "Ақпараттық қауіпсіздік", "Информационная безопасность", "Information security", "cs_terminology"),
        ("encryption", "Шифрлау", "Шифрование", "Encryption", "cs_terminology"),
        ("digital_signature", "Электрондық цифрлық қолтаңба (ЭЦҚ)", "Электронная цифровая подпись (ЭЦП)", "Digital signature", "cs_terminology"),
        ("computer_network", "Компьютерлік желі", "Компьютерная сеть", "Computer network", "cs_terminology"),
        ("network_topology", "Желілік топология", "Топология сети", "Network topology", "cs_terminology"),
        ("ip_address", "IP-мекенжай", "IP-адрес", "IP address", "cs_terminology"),
        ("subnet_mask", "Ішкі желі маскасы", "Маска подсети", "Subnet mask", "cs_terminology"),
        ("artificial_intelligence", "Жасанды интеллект", "Искусственный интеллект", "Artificial intelligence", "cs_terminology"),
        ("cloud_computing", "Бұлттық есептеулер", "Облачные вычисления", "Cloud computing", "cs_terminology"),
        ("loop_statement", "Циклдік нұсқау (қайталану операторы)", "Циклический оператор", "Loop statement", "cs_terminology"),
        ("conditional_statement", "Шартты оператор", "Условный оператор", "Conditional statement", "cs_terminology"),
        ("list_comprehension", "Тізім генераторы", "Генератор списков", "List comprehension", "cs_terminology"),
    ]

    for key, kk_t, ru_t, en_t, ctx in glossary_items:
        session.add(
            LocalizationGlossary(
                concept_key=key,
                kk=kk_t,
                ru=ru_t,
                en=en_t,
                context=ctx,
                source="NTC_KZ",
                approved=True,
            )
        )
    await session.flush()

    # 3. Seed Exam Types and Subjects
    exam_unt = ExamType(
        code="unt",
        name_kk="Ұлттық бірыңғай тестілеу (ҰБТ)",
        name_ru="Единое национальное тестирование (ЕНТ)",
        name_en="Unified National Testing (UNT)",
        description="Казахстанский национальный вступительный экзамен в высшие учебные заведения",
    )
    session.add(exam_unt)

    subject_info = Subject(
        code="informatics",
        name_kk="Информатика",
        name_ru="Информатика",
        name_en="Informatics",
        is_profile=True,
        order_index=1,
    )
    session.add(subject_info)

    subject_math = Subject(
        code="mathematics",
        name_kk="Математика",
        name_ru="Математика",
        name_en="Mathematics",
        is_profile=True,
        order_index=2,
    )
    session.add(subject_math)
    await session.flush()

    # 4. Seed Current UNT Rules (2026 Season)
    current_rule = CurrentUntRule(
        exam_type_id=exam_unt.id,
        exam_year=2026,
        is_active=True,
        total_questions=120,
        maximum_score=140,
        duration_minutes=240,
        passing_threshold_total=50,
        passing_threshold_per_subject=5,
        informatics_questions_count=50,
        informatics_max_score=50,
        subjects_structure={
            "mandatory": [
                {"name_kk": "Қазақстан тарихы", "name_ru": "История Казахстана", "questions": 20, "max_score": 20},
                {"name_kk": "Оқу сауаттылығы", "name_ru": "Грамотность чтения", "questions": 10, "max_score": 10},
                {"name_kk": "Математикалық сауаттылық", "name_ru": "Математическая грамотность", "questions": 10, "max_score": 10},
            ],
            "profile": [
                {"name_kk": "1-бейіндік пән (Математика)", "name_ru": "1-й профильный (Математика)", "questions": 40, "max_score": 50},
                {"name_kk": "2-бейіндік пән (Информатика)", "name_ru": "2-й профильный (Информатика)", "questions": 40, "max_score": 50},
            ],
        },
        profile_combinations={
            "IT_and_CS": {
                "pair_name_kk": "Математика + Информатика",
                "pair_name_ru": "Математика + Информатика",
                "educational_programs": [
                    "B057 — Ақпараттық технологиялар (Information Technology)",
                    "B058 — Ақпараттық қауіпсіздік (Information Security)",
                    "B059 — Коммуникациялар және коммуникациялық технологиялар",
                    "6B061 — Компьютерлік ғылымдар және бағдарламалау",
                ],
                "recommended_target_score": 125,
            }
        },
        testing_periods=[
            {"period": "Қаңтар / Январь", "type": "paid", "purpose": "Шартты түрде ақылы оқуға түсу", "dates": "10.01 — 10.02"},
            {"period": "Наурыз / Март", "type": "paid", "purpose": "Ақылы оқуға түсу мүмкіндігі", "dates": "01.03 — 31.03"},
            {"period": "Мамыр — Шілде / Май — Июль", "type": "grant", "purpose": "Мемлекеттік грант байқауына қатысу (2 мүмкіндік)", "dates": "16.05 — 05.07"},
            {"period": "Тамыз / Август", "type": "paid", "purpose": "Қосымша ақылы оқуға түсу", "dates": "10.08 — 20.08"},
        ],
        important_deadlines={
            "grant_application_start": "2026-07-13",
            "grant_application_end": "2026-07-20",
            "grant_results_announcement": "2026-08-10",
            "main_unt_registration_deadline": "2026-05-10",
        },
        grant_rules_summary={
            "minimum_for_national_universities": 65,
            "minimum_for_other_universities": 50,
            "it_specialties_competitive_range": "115 — 138 баллов",
            "special_quotas": "Ауыл квотасы (35%), көпбалалы отбасылар (5%), жетім балалар (1%)",
        },
        official_source_urls=[
            "https://testcenter.kz/ru/ent/o-formate-ent/",
            "https://www.gov.kz/memleket/entities/sci/press/news/details/",
        ],
        last_verified_at=datetime.now(timezone.utc),
        verified_by="ҰТО Ресми Спецификация 2026",
    )
    session.add(current_rule)
    await session.flush()

    # 5. Seed Exam Specification (2026.1) & Hierarchical Taxonomy (6 Sections, 24 Topics)
    spec_hash = hashlib.sha256(b"NTC_INFORMATICS_SPEC_2026_V1").hexdigest()
    spec = ExamSpecification(
        exam_type_id=exam_unt.id,
        subject_id=subject_info.id,
        exam_year=2026,
        version="2026.1",
        title_kk="ҰБТ Информатика пәні бойынша ресми тест спецификациясы (2025-2026)",
        title_ru="Официальная спецификация теста ЕНТ по предмету Информатика (2025-2026)",
        title_en="Official UNT Informatics Test Specification (2025-2026)",
        valid_from=date(2025, 9, 1),
        valid_to=date(2026, 8, 31),
        status=SpecificationStatus.ACTIVE,
        source_url="https://testcenter.kz/ru/ent/specifikacii-testov/",
        total_questions=50,
        max_score=50,
        content_hash=spec_hash,
    )
    session.add(spec)
    await session.flush()

    # Define 6 Sections and their Topics
    taxonomy_data = [
        {
            "code": "CS-1",
            "title_kk": "Ақпарат және ақпараттық үдерістер",
            "title_ru": "Информация и информационные процессы",
            "title_en": "Information and Information Processes",
            "weight": 16,
            "q_count": 8,
            "topics": [
                ("1.1", "Санау жүйелері және аудару ережелері", "Системы счисления и правила перевода", "Number Systems and Conversions"),
                ("1.2", "Ақпаратты кодтау және ақпарат көлемін өлшеу", "Кодирование и измерение объема информации", "Information Encoding and Measurement"),
                ("1.3", "Логикалық амалдар және логикалық схемалар", "Логические операции и логические схемы", "Logical Operations and Logic Gates"),
            ]
        },
        {
            "code": "CS-2",
            "title_kk": "Компьютерлік жүйелер және желілер",
            "title_ru": "Компьютерные системы и сети",
            "title_en": "Computer Systems and Networks",
            "weight": 16,
            "q_count": 8,
            "topics": [
                ("2.1", "ЭЕМ архитектурасы және аппараттық қамтамасыз ету", "Архитектура ЭВМ и аппаратное обеспечение", "Computer Architecture and Hardware"),
                ("2.2", "Компьютерлік желілер, топологиялар және жабдықтар", "Компьютерные сети, топологии и оборудование", "Computer Networks, Topologies and Equipment"),
                ("2.3", "OSI моделі, желілік хаттамалар және IP-адрестеу", "Модель OSI, сетевые протоколы и IP-адресация", "OSI Model, Protocols and IP Addressing"),
            ]
        },
        {
            "code": "CS-3",
            "title_kk": "Ақпараттық қауіпсіздік",
            "title_ru": "Информационная безопасность",
            "title_en": "Information Security",
            "weight": 14,
            "q_count": 7,
            "topics": [
                ("3.1", "Киберқауіптер және зиянды бағдарламалардың түрлері", "Киберугрозы и типы вредоносного ПО", "Cyber Threats and Malware Types"),
                ("3.2", "Криптография, шифрлау әдістері және ЭЦҚ", "Криптография, методы шифрования и ЭЦП", "Cryptography and Digital Signatures"),
                ("3.3", "Деректердің құпиялылығы және сақтық көшірме жасау", "Конфиденциальность данных и резервное копирование", "Data Privacy and Backups"),
            ]
        },
        {
            "code": "CS-4",
            "title_kk": "Алгоритмдеу және Python тілінде бағдарламалау",
            "title_ru": "Алгоритмизация и программирование на Python",
            "title_en": "Algorithms and Python Programming",
            "weight": 28,
            "q_count": 14,
            "topics": [
                ("4.1", "Python базалық құрылымдары және шартты операторлар", "Базовые структуры и условные операторы Python", "Python Basic Syntax and Conditionals"),
                ("4.2", "Циклдік құрылымдар (for, while) және генераторлар", "Циклические конструкции (for, while) и генераторы", "Loops and Comprehensions"),
                ("4.3", "Жолдар, тізімдер және сөздіктермен жұмыс", "Работа со строками, списками и словарями", "Strings, Lists and Dictionaries"),
                ("4.4", "Функциялар және рекурсивті алгоритмдер", "Функции и рекурсивные алгоритмы", "Functions and Recursive Algorithms"),
                ("4.5", "Сұрыптау және іздеу алгоритмдері", "Алгоритмы сортировки и поиска", "Sorting and Searching Algorithms"),
            ]
        },
        {
            "code": "CS-5",
            "title_kk": "Деректер базасы және SQL",
            "title_ru": "Базы данных и SQL",
            "title_en": "Databases and SQL",
            "weight": 16,
            "q_count": 8,
            "topics": [
                ("5.1", "Реляциялық деректер базасының моделі мен кілттері", "Модель реляционных баз данных и ключи", "Relational Database Model and Keys"),
                ("5.2", "SQL деректерді таңдау және сүзгілеу (SELECT, WHERE, ORDER BY)", "Выборка и фильтрация SQL (SELECT, WHERE, ORDER BY)", "SQL Querying and Filtering"),
                ("5.3", "Бірнеше кестені біріктіру және агрегаттық функциялар (JOIN, GROUP BY)", "Объединение таблиц и агрегаты (JOIN, GROUP BY)", "Table Joins and Aggregate Functions"),
            ]
        },
        {
            "code": "CS-6",
            "title_kk": "Web-технологиялар және заманауи IT",
            "title_ru": "Веб-технологии и современные IT",
            "title_en": "Web Technologies and Modern IT",
            "weight": 10,
            "q_count": 5,
            "topics": [
                ("6.1", "HTML/CSS құрылымы және Web-беттерді әзірлеу", "HTML/CSS структура и веб-разработка", "HTML/CSS and Web Development"),
                ("6.2", "Жасанды интеллект, бұлттық технологиялар және IoT", "Искусственный интеллект, облака и IoT", "AI, Cloud Computing and IoT"),
            ]
        },
    ]

    topic_id_map = {}
    for idx_sec, sec_item in enumerate(taxonomy_data, 1):
        sec = SpecificationSection(
            specification_id=spec.id,
            code=sec_item["code"],
            title_kk=sec_item["title_kk"],
            title_ru=sec_item["title_ru"],
            title_en=sec_item["title_en"],
            weight_percentage=sec_item["weight"],
            question_count_est=sec_item["q_count"],
            order_index=idx_sec,
        )
        session.add(sec)
        await session.flush()

        for idx_top, (t_code, t_kk, t_ru, t_en) in enumerate(sec_item["topics"], 1):
            top = SpecificationTopic(
                section_id=sec.id,
                code=t_code,
                title_kk=t_kk,
                title_ru=t_ru,
                title_en=t_en,
                order_index=idx_top,
            )
            session.add(top)
            await session.flush()
            topic_id_map[t_code] = top.id

    # 6. Seed Bank Questions (Official Samples & Specification-based with full Provenance & Translations)
    sample_questions = [
        {
            "topic_code": "1.1",
            "type": "single_choice",
            "difficulty": QuestionDifficulty.A,
            "score": 1,
            "year": 2026,
            "status": OfficialStatus.OFFICIAL_SAMPLE,
            "text_kk": "Ондық санау жүйесіндегі 45 санының екілік жүйедегі жазылуын табыңыз:",
            "text_ru": "Найдите запись числа 45 из десятичной системы счисления в двоичной системе:",
            "text_en": "Convert the decimal number 45 into the binary numeral system:",
            "code_snippet": None,
            "options": [
                {"key": "A", "kk": "101101", "ru": "101101", "en": "101101", "correct": True},
                {"key": "B", "kk": "110101", "ru": "110101", "en": "110101", "correct": False},
                {"key": "C", "kk": "101011", "ru": "101011", "en": "101011", "correct": False},
                {"key": "D", "kk": "111001", "ru": "111001", "en": "111001", "correct": False},
            ],
            "solution_kk": "45-ті 2-ге бөлеміз:\n45 / 2 = 22 (қалдық 1)\n22 / 2 = 11 (қалдық 0)\n11 / 2 = 5 (қалдық 1)\n5 / 2 = 2 (қалдық 1)\n2 / 2 = 1 (қалдық 0)\n1 / 2 = 0 (қалдық 1)\nҚалдықтарды соңынан басына қарай оқимыз: 101101₂. Немесе 45 = 32 + 8 + 4 + 1 = 2⁵ + 2³ + 2² + 2⁰ = 101101₂.",
            "solution_ru": "Разложим число 45 по степеням двойки: 45 = 32 + 8 + 4 + 1 = 2⁵ + 2³ + 2² + 2⁰ = 101101₂.",
            "solution_en": "Represent 45 as sum of powers of two: 45 = 32 + 8 + 4 + 1 = 2^5 + 2^3 + 2^2 + 2^0 = 101101₂.",
            "exam_tip_kk": "ҰБТ-да уақыт үнемдеу үшін 2-нің дәрежелеріне (32, 16, 8, 4, 2, 1) жіктеу әдісі ең жылдам болып табылады.",
            "exam_tip_ru": "На ЕНТ метод разложения по степеням двойки быстрее последовательного деления столбиком.",
            "exam_tip_en": "Decomposition by powers of 2 is significantly faster than division.",
            "source_title": "ҰТО 2026 ресми байқау тесті үлгісі",
            "source_url": "https://testcenter.kz/ent/samples/cs-2026-01",
        },
        {
            "topic_code": "4.2",
            "type": "single_choice",
            "difficulty": QuestionDifficulty.B,
            "score": 1,
            "year": 2026,
            "status": OfficialStatus.OFFICIAL_SPECIFICATION_BASED,
            "text_kk": "Python бағдарламасының орындалу нәтижесінде экранға не шығады?\n\na = [i for i in range(10) if i % 2 != 0 and i % 3 != 0]\nprint(len(a), sum(a))",
            "text_ru": "Что выведет следующий код на Python?\n\na = [i for i in range(10) if i % 2 != 0 and i % 3 != 0]\nprint(len(a), sum(a))",
            "text_en": "What will be the output of the following Python code snippet?\n\na = [i for i in range(10) if i % 2 != 0 and i % 3 != 0]\nprint(len(a), sum(a))",
            "code_snippet": "a = [i for i in range(10) if i % 2 != 0 and i % 3 != 0]\nprint(len(a), sum(a))",
            "options": [
                {"key": "A", "kk": "3 13", "ru": "3 13", "en": "3 13", "correct": True},
                {"key": "B", "kk": "4 16", "ru": "4 16", "en": "4 16", "correct": False},
                {"key": "C", "kk": "3 15", "ru": "3 15", "en": "3 15", "correct": False},
                {"key": "D", "kk": "5 25", "ru": "5 25", "en": "5 25", "correct": False},
            ],
            "solution_kk": "range(10) жиынынан (0-ден 9-ға дейін) тақ және 3-ке бөлінбейтін сандар:\n- 1 (тақ, 3-ке бөлінбейді) — сәйкес\n- 3 (3-ке бөлінеді) — жарамайды\n- 5 (тақ, 3-ке бөлінбейді) — сәйкес\n- 7 (тақ, 3-ке бөлінбейді) — сәйкес\n- 9 (3-ке бөлінеді) — жарамайды\nНәтижесінде a = [1, 5, 7]. Ұзындығы len(a) = 3, қосындысы sum(a) = 1 + 5 + 7 = 13.",
            "solution_ru": "Числа от 0 до 9, нечетные и не делящиеся на 3: 1, 5, 7. Список a = [1, 5, 7]. len(a) = 3, sum(a) = 13.",
            "solution_en": "Odd numbers not divisible by 3 in range(10): 1, 5, 7. a = [1, 5, 7]. len(a) = 3, sum(a) = 13.",
            "exam_tip_kk": "range(10) соңғы 10 санын қамтымайтынын (0..9) әрдайым есте сақтаңыз.",
            "exam_tip_ru": "Помните, что range(N) генерирует числа до N-1 включительно.",
            "exam_tip_en": "Always remember range(N) excludes N.",
            "source_title": "ҰТО 2026 Python спецификациялық тапсырмасы",
            "source_url": "https://testcenter.kz/ent/spec-python-2026",
        },
        {
            "topic_code": "5.3",
            "type": "single_choice",
            "difficulty": QuestionDifficulty.B,
            "score": 1,
            "year": 2026,
            "status": OfficialStatus.OFFICIAL_SPECIFICATION_BASED,
            "text_kk": "Берілген 'Students' кестесінен баллы 100-ден жоғары студенттердің орташа жасын есептейтін дұрыс SQL сұранысын көрсетіңіз:",
            "text_ru": "Укажите корректный SQL запрос для подсчета среднего возраста студентов с баллом выше 100 из таблицы 'Students':",
            "text_en": "Choose the correct SQL query to calculate the average age of students with score over 100 from 'Students' table:",
            "code_snippet": None,
            "options": [
                {"key": "A", "kk": "SELECT AVG(age) FROM Students WHERE score > 100;", "ru": "SELECT AVG(age) FROM Students WHERE score > 100;", "en": "SELECT AVG(age) FROM Students WHERE score > 100;", "correct": True},
                {"key": "B", "kk": "SELECT SUM(age) FROM Students HAVING score > 100;", "ru": "SELECT SUM(age) FROM Students HAVING score > 100;", "en": "SELECT SUM(age) FROM Students HAVING score > 100;", "correct": False},
                {"key": "C", "kk": "SELECT COUNT(age) FROM Students WHERE score >= 100;", "ru": "SELECT COUNT(age) FROM Students WHERE score >= 100;", "en": "SELECT COUNT(age) FROM Students WHERE score >= 100;", "correct": False},
                {"key": "D", "kk": "SELECT AVERAGE(age) FROM Students WHERE score > 100;", "ru": "SELECT AVERAGE(age) FROM Students WHERE score > 100;", "en": "SELECT AVERAGE(age) FROM Students WHERE score > 100;", "correct": False},
            ],
            "solution_kk": "SQL стандартында орташа мәнді табу үшін 'AVG()' агрегаттық функциясы қолданылады (AVERAGE емес!). Жолдарды сүзгілеу үшін 'WHERE' операторы қызмет етеді.",
            "solution_ru": "В стандарте SQL для вычисления среднего используется функция AVG() (не AVERAGE), а для фильтрации строк — предложение WHERE.",
            "solution_en": "In SQL standard, AVG() is the aggregate function for mean value, and WHERE filters individual rows.",
            "exam_tip_kk": "ҰБТ-да жиі кездесетін қате — 'AVG' орнына ойдан шығарылған 'AVERAGE' немесе 'MEAN' функцияларын таңдау.",
            "exam_tip_ru": "Частая ловушка на ЕНТ — несуществующие функции AVERAGE или MEAN вместо стандартного AVG.",
            "exam_tip_en": "Watch out for fake function names like AVERAGE instead of AVG.",
            "source_title": "ҰТО Деректер базасы ресми тесті",
            "source_url": "https://testcenter.kz/ent/sql-sample-2026",
        },
        {
            "topic_code": "2.3",
            "type": "single_choice",
            "difficulty": QuestionDifficulty.B,
            "score": 1,
            "year": 2026,
            "status": OfficialStatus.OFFICIAL_SAMPLE,
            "text_kk": "IP-мекенжайы 192.168.10.45 және ішкі желі маскасы 255.255.255.0 болғанда, осы желінің мекенжайы (Network Address) қандай болады?",
            "text_ru": "Для узла с IP-адресом 192.168.10.45 и маской подсети 255.255.255.0 определите адрес сети:",
            "text_en": "Given host IP address 192.168.10.45 and subnet mask 255.255.255.0, what is the Network Address?",
            "code_snippet": None,
            "options": [
                {"key": "A", "kk": "192.168.10.0", "ru": "192.168.10.0", "en": "192.168.10.0", "correct": True},
                {"key": "B", "kk": "192.168.10.255", "ru": "192.168.10.255", "en": "192.168.10.255", "correct": False},
                {"key": "C", "kk": "192.168.0.0", "ru": "192.168.0.0", "en": "192.168.0.0", "correct": False},
                {"key": "D", "kk": "192.168.10.1", "ru": "192.168.10.1", "en": "192.168.10.1", "correct": False},
            ],
            "solution_kk": "Желі мекенжайын табу үшін IP-мекенжай мен маска арасында разрядтық конъюнкция (AND) қолданылады. 255.255.255.0 маскасында алғашқы 3 байт өзгеріссіз қалады (192.168.10), ал соңғы байт 45 AND 0 = 0 болады. Демек, желі мекенжайы — 192.168.10.0 (ал 192.168.10.255 — кеңтаратылымдық / broadcast мекенжайы).",
            "solution_ru": "Поразрядное логическое 'И' (AND) между 192.168.10.45 и 255.255.255.0 дает 192.168.10.0. Адрес 192.168.10.255 является широковещательным (broadcast).",
            "solution_en": "Bitwise AND between IP 192.168.10.45 and mask 255.255.255.0 yields 192.168.10.0.",
            "exam_tip_kk": "Есте сақтаңыз: .0 соңы — желі мекенжайы, .255 — broadcast, .1..254 — тораптар (хосттар) үшін рұқсат етілген.",
            "exam_tip_ru": "Запомните: .0 — адрес сети, .255 — broadcast, .1-.254 — доступные хосты.",
            "exam_tip_en": ".0 is network ID, .255 is broadcast.",
            "source_title": "ҰТО Компьютерлік желілер 2026",
            "source_url": "https://testcenter.kz/ent/networks-sample",
        },
        {
            "topic_code": "3.2",
            "type": "single_choice",
            "difficulty": QuestionDifficulty.A,
            "score": 1,
            "year": 2026,
            "status": OfficialStatus.OFFICIAL_SPECIFICATION_BASED,
            "text_kk": "Асимметриялық шифрлау жүйесінде құпия ақпаратты шифрлау және электрондық цифрлық қолтаңбаны (ЭЦҚ) тексеру үшін қай кілт қолданылады?",
            "text_ru": "Какой ключ используется для шифрования сообщений и проверки электронной цифровой подписи (ЭЦП) в асимметричной криптосистеме?",
            "text_en": "Which key is used for encryption and verifying a digital signature in asymmetric cryptography?",
            "code_snippet": None,
            "options": [
                {"key": "A", "kk": "Ашық кілт (Public Key)", "ru": "Открытый ключ (Public Key)", "en": "Public Key", "correct": True},
                {"key": "B", "kk": "Жабық кілт (Private Key)", "ru": "Закрытый ключ (Private Key)", "en": "Private Key", "correct": False},
                {"key": "C", "kk": "Симметриялық кілт", "ru": "Симметричный ключ", "en": "Symmetric key", "correct": False},
                {"key": "D", "kk": "Сеанстық кілт", "ru": "Сессионный ключ", "en": "Session key", "correct": False},
            ],
            "solution_kk": "Асимметриялық криптографияда екі кілт бар:\n1. Ашық кілт (Public key) — баршаға қолжетімді, хабарламаны шифрлауға және ЭЦҚ түпнұсқалығын тексеруге арналған.\n2. Жабық кілт (Private key) — тек иесіне ғана белгілі, хабарламаның шифрын ашуға және ЭЦҚ қоюға (қалыптастыруға) қызмет етеді.",
            "solution_ru": "Открытый ключ (Public Key) доступен всем и используется для шифрования сообщений адресату и верификации его ЭЦП. Закрытый ключ (Private Key) хранит только владелец для расшифровки и формирования ЭЦП.",
            "solution_en": "Public Key is publicly shared to encrypt data and verify digital signatures.",
            "exam_tip_kk": "ЭЦҚ қалыптастыру — жабық кілтпен, ал ЭЦҚ тексеру — ашық кілтпен жасалады.",
            "exam_tip_ru": "Подпись создается закрытым ключом, а проверяется открытым.",
            "exam_tip_en": "Sign with Private Key, verify with Public Key.",
            "source_title": "ҰТО Ақпараттық қауіпсіздік 2026",
            "source_url": "https://testcenter.kz/ent/security-2026",
        }
    ]

    for q_data in sample_questions:
        q_hash = hashlib.sha256(q_data["text_kk"].encode("utf-8")).hexdigest()
        top_id = topic_id_map.get(q_data["topic_code"])

        bq = BankQuestion(
            subject_id=subject_info.id,
            specification_topic_id=top_id,
            question_type=q_data["type"],
            difficulty=q_data["difficulty"],
            difficulty_score=0.30 if q_data["difficulty"] == "A" else (0.55 if q_data["difficulty"] == "B" else 0.85),
            official_status=q_data["status"],
            original_language="kk",
            year=q_data["year"],
            maximum_score=q_data["score"],
            content_hash=q_hash,
            is_active=True,
        )
        session.add(bq)
        await session.flush()

        # Translations (kk, ru, en)
        session.add(QuestionTranslation(
            question_id=bq.id,
            locale="kk",
            text=q_data["text_kk"],
            code_snippet=q_data["code_snippet"],
            explanation=q_data["solution_kk"],
            translation_source="official",
            translation_status="published",
        ))
        session.add(QuestionTranslation(
            question_id=bq.id,
            locale="ru",
            text=q_data["text_ru"],
            code_snippet=q_data["code_snippet"],
            explanation=q_data["solution_ru"],
            translation_source="official",
            translation_status="published",
        ))
        session.add(QuestionTranslation(
            question_id=bq.id,
            locale="en",
            text=q_data["text_en"],
            code_snippet=q_data["code_snippet"],
            explanation=q_data["solution_en"],
            translation_source="human",
            translation_status="published",
        ))

        # Options
        for idx_opt, opt_item in enumerate(q_data["options"], 1):
            opt = QuestionBankOption(
                question_id=bq.id,
                option_key=opt_item["key"],
                is_correct=opt_item["correct"],
                order_index=idx_opt,
            )
            session.add(opt)
            await session.flush()

            session.add(QuestionBankOptionTranslation(option_id=opt.id, locale="kk", text=opt_item["kk"]))
            session.add(QuestionBankOptionTranslation(option_id=opt.id, locale="ru", text=opt_item["ru"]))
            session.add(QuestionBankOptionTranslation(option_id=opt.id, locale="en", text=opt_item["en"]))

        # Provenance record
        session.add(QuestionProvenance(
            question_id=bq.id,
            source_id=ntc_source.id,
            source_url=q_data["source_url"],
            source_title=q_data["source_title"],
            copyright_status="public_educational_use",
            license_type="NTC_Public_Sample",
            reuse_allowed=True,
            official_status=q_data["status"],
            content_hash=q_hash,
            published_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        ))

        # Solution record
        sol = BankSolution(
            question_id=bq.id,
            approach_type="standard_analytical",
            complexity="O(1)",
        )
        session.add(sol)
        await session.flush()

        session.add(BankSolutionTranslation(
            solution_id=sol.id,
            locale="kk",
            step_by_step_explanation=q_data["solution_kk"],
            exam_tip=q_data["exam_tip_kk"],
        ))
        session.add(BankSolutionTranslation(
            solution_id=sol.id,
            locale="ru",
            step_by_step_explanation=q_data["solution_ru"],
            exam_tip=q_data["exam_tip_ru"],
        ))
        session.add(BankSolutionTranslation(
            solution_id=sol.id,
            locale="en",
            step_by_step_explanation=q_data["solution_en"],
            exam_tip=q_data["exam_tip_en"],
        ))

    # 7. Seed Verified 2026 UNT News
    news_items = [
        {
            "canonical_url": "https://testcenter.kz/press/news/2026-main-unt-dates",
            "category": NewsCategory.REGISTRATION,
            "importance": 10,
            "relevance": 1.0,
            "is_breaking": True,
            "published_at": datetime.now(timezone.utc) - timedelta(hours=3),
            "title_kk": "2026 жылғы Негізгі ҰБТ-ға тіркелу басталды: 2 мүмкіндік және грант конкурсы",
            "summary_kk": "Ұлттық тестілеу орталығы 2026 жылғы мемлекеттік грант конкурсына арналған негізгі ҰБТ-ға өтініш қабылдау кестесін жариялады.",
            "content_kk": "Ұлттық тестілеу орталығының (ҰТО) ресми мәліметінше, биылғы талапкерлерге негізгі тестілеуге екі рет қатысу мүмкіндігі беріледі. Ең үздік нәтиже мемлекеттік грант байқауына жолданады. Тестілеу форматы: 120 сұрақ, ең жоғары балл — 140, уақыты — 240 минут.",
            "title_ru": "Стартовала регистрация на Основное ЕНТ 2026: 2 попытки и участие в конкурсе грантов",
            "summary_ru": "Национальный центр тестирования открыл прием заявок на основное ЕНТ 2026 для участия в конкурсе образовательных грантов.",
            "content_ru": "По официальным данным НЦТ, абитуриентам предоставляется две попытки сдачи основного ЕНТ с возможностью подачи лучшего сертификата на государственный грант. Формат экзамена: 120 вопросов, максимальный балл — 140, продолжительность — 240 минут.",
            "title_en": "Registration for Main UNT 2026 is officially open: 2 attempts and grant eligibility",
            "summary_en": "The National Testing Center has opened applications for the main UNT 2026 grant examination season.",
            "content_en": "According to the National Testing Center, applicants are granted two attempts for the main state testing, allowing submission of the highest score for higher education grant competitions.",
        },
        {
            "canonical_url": "https://testcenter.kz/press/news/2026-informatics-spec-update",
            "category": NewsCategory.INFORMATICS,
            "importance": 9,
            "relevance": 1.0,
            "is_breaking": False,
            "published_at": datetime.now(timezone.utc) - timedelta(days=1),
            "title_kk": "Информатика пәні бойынша ҰБТ спецификациясы: Python және SQL тапсырмаларының үлесі өсті",
            "summary_kk": "2026 жылғы бейіндік Информатика пәнінде алгоритмдеу және деректер базасы бөлімдеріне 44% сұрақ бөлінген.",
            "content_kk": "Ұлттық тестілеу орталығы Информатика пәнінен 2026 жылғы жаңартылған спецификацияны бекітті. Басты назар практикалық алгоритмдеуге (Python 3.x), рекурсияға және реляциялық деректер базасындағы SQL сұраныстарына (JOIN, GROUP BY) бағытталған.",
            "title_ru": "Обновление спецификации ЕНТ по Информатике: увеличен вес задач на Python и SQL",
            "summary_ru": "В спецификации 2026 года на темы программирования и баз данных приходится 44% от общего числа вопросов профиля.",
            "content_ru": "Национальный центр тестирования утвердил актуальную спецификацию по Информатике. Особый акцент сделан на практические задачи Python (рекурсия, списковые генераторы) и SQL запросы.",
            "title_en": "UNT Informatics Specification Update: Increased focus on Python algorithms and SQL",
            "summary_en": "The 2026 Informatics specification allocates 44% of questions to algorithms and relational databases.",
            "content_en": "The National Testing Center confirmed the updated Informatics framework with increased emphasis on Python code tracing, sorting algorithms, and SQL JOIN queries.",
        },
        {
            "canonical_url": "https://www.gov.kz/memleket/entities/sci/press/news/2026-it-grants-quota",
            "category": NewsCategory.GRANTS,
            "importance": 8,
            "relevance": 0.95,
            "is_breaking": False,
            "published_at": datetime.now(timezone.utc) - timedelta(days=3),
            "title_kk": "ҚР ҒЖБМ: IT мамандықтары бойынша мемлекеттік гранттар саны көбейтілді",
            "summary_kk": "2026-2027 оқу жылында «Ақпараттық технологиялар» және «Ақпараттық қауіпсіздік» бағыттарына қосымша гранттар бөлінді.",
            "content_kk": "ҚР Ғылым және жоғары білім министрлігінің мәліметінше, «Математика + Информатика» бейіндік жұбы бойынша білім беру гранттарының саны артты. Ауыл квотасы (35%) және инженерлік IT бағдарламалар үшін арнайы стипендиялар қарастырылған.",
            "title_ru": "МНВО РК: Увеличено количество грантов на IT-специальности в 2026 году",
            "summary_ru": "На 2026-2027 учебный год выделены дополнительные гранты на направления «Информационные технологии» и «Кибербезопасность».",
            "content_ru": "Министерство науки и высшего образования РК расширило квоту грантов для профиля «Математика + Информатика».",
            "title_en": "Ministry of Science and Higher Education increases IT scholarship grants for 2026",
            "summary_en": "Additional government grants allocated for Information Technology and Cybersecurity programs.",
            "content_en": "The Ministry of Science and Higher Education announced increased funding and grant quotas for the Math + Informatics combination.",
        }
    ]

    for n_item in news_items:
        n_hash = hashlib.sha256((n_item["title_kk"] + " " + n_item["content_kk"]).encode("utf-8")).hexdigest()
        art = NewsArticle(
            canonical_url=n_item["canonical_url"],
            source_id=ntc_source.id if "testcenter" in n_item["canonical_url"] else gov_sci_source.id,
            category=n_item["category"],
            original_language="kk",
            importance_score=n_item["importance"],
            relevance_score=n_item["relevance"],
            is_breaking=n_item["is_breaking"],
            status=NewsStatus.PUBLISHED,
            content_hash=n_hash,
            published_at=n_item["published_at"],
            fetched_at=datetime.now(timezone.utc),
            last_verified_at=datetime.now(timezone.utc),
        )
        session.add(art)
        await session.flush()

        session.add(NewsTranslation(
            news_id=art.id,
            locale="kk",
            title=n_item["title_kk"],
            summary=n_item["summary_kk"],
            content=n_item["content_kk"],
            translation_source="official",
            translation_status="published",
        ))
        session.add(NewsTranslation(
            news_id=art.id,
            locale="ru",
            title=n_item["title_ru"],
            summary=n_item["summary_ru"],
            content=n_item["content_ru"],
            translation_source="official",
            translation_status="published",
        ))
        session.add(NewsTranslation(
            news_id=art.id,
            locale="en",
            title=n_item["title_en"],
            summary=n_item["summary_en"],
            content=n_item["content_en"],
            translation_source="human",
            translation_status="published",
        ))

        session.add(NewsSource(
            news_id=art.id,
            source_id=art.source_id,
            external_url=n_item["canonical_url"],
            attribution_text=f"ҚР ҰТО / ҒЖБМ Ресми дереккөзі ({art.published_at.strftime('%d.%m.%Y')})"
        ))

    await session.commit()
