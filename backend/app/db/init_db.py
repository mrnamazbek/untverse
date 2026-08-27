from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserProfile, UserRole
from app.models.course import Course, Topic, Lesson
from app.models.quiz import Quiz, Question, QuestionOption, QuizType, QuestionType
from app.models.coding import CodingTask, TestCase
from app.models.gamification import Achievement, DailyMission
from app.core.security import get_password_hash


async def _seed_base_data(session: AsyncSession):
    # 1. Seed Users (Admin & Demo Student)
    admin_user = User(
        email="admin@unt-informatics.kz",
        hashed_password=get_password_hash("admin12345"),
        role=UserRole.ADMIN.value,
        is_active=True,
        is_verified=True,
    )
    session.add(admin_user)
    await session.flush()

    admin_profile = UserProfile(
        user_id=admin_user.id,
        display_name="Главный Методист ЕНТ",
        bio="Администратор и разработчик экзаменационных материалов по информатике",
        target_unt_score=50,
        current_level=25,
        total_xp=25000,
        rank_title="Магистр Информатики ЕНТ",
        streak_count=14,
    )
    session.add(admin_profile)

    demo_student = User(
        email="student@unt-informatics.kz",
        hashed_password=get_password_hash("student12345"),
        role=UserRole.STUDENT.value,
        is_active=True,
        is_verified=True,
    )
    session.add(demo_student)
    await session.flush()

    student_profile = UserProfile(
        user_id=demo_student.id,
        display_name="Алихан Смагулов",
        bio="Готовлюсь к сдаче ЕНТ по профилю Информатика на 50/50 баллов!",
        target_unt_score=48,
        current_level=3,
        total_xp=620,
        rank_title="Студент-Исследователь",
        streak_count=4,
    )
    session.add(student_profile)

    # 2. Seed Achievements
    achievements_data = [
        {"code": "first_lesson", "title": "Первый шаг к успеху", "description": "Пройти свой первый теоретический урок", "icon": "book-open", "badge_color": "blue", "category": "learning", "xp_reward": 50, "condition_type": "lessons_count", "condition_value": 1},
        {"code": "first_quiz", "title": "Боевое крещение", "description": "Успешно завершить первый тест по информатике", "icon": "check-circle", "badge_color": "green", "category": "quizzes", "xp_reward": 50, "condition_type": "quizzes_count", "condition_value": 1},
        {"code": "perfect_quiz_first", "title": "Абсолютная точность", "description": "Сдать любой тест на 100% без единой ошибки", "icon": "zap", "badge_color": "orange", "category": "mastery", "xp_reward": 100, "condition_type": "perfect_quizzes", "condition_value": 1},
        {"code": "first_code_task", "title": "Привет, Python!", "description": "Решить первую задачу по программированию с прохождением всех тестов", "icon": "code", "badge_color": "purple", "category": "coding", "xp_reward": 75, "condition_type": "coding_solved", "condition_value": 1},
        {"code": "streak_3", "title": "Набираем темп", "description": "Удерживать ежедневный стрик обучения 3 дня подряд", "icon": "flame", "badge_color": "orange", "category": "streaks", "xp_reward": 100, "condition_type": "streak_days", "condition_value": 3},
        {"code": "streak_7", "title": "Недельный марафонец", "description": "Удерживать непрерывный стрик обучения 7 дней подряд", "icon": "flame", "badge_color": "pink", "category": "streaks", "xp_reward": 250, "condition_type": "streak_days", "condition_value": 7},
        {"code": "streak_30", "title": "Легенда дисциплины", "description": "Удерживать стрик 30 дней подряд", "icon": "crown", "badge_color": "purple", "category": "streaks", "xp_reward": 1000, "condition_type": "streak_days", "condition_value": 30},
        {"code": "level_5", "title": "Ученик 5 уровня", "description": "Достичь 5-го уровня в профиле", "icon": "award", "badge_color": "sky", "category": "general", "xp_reward": 150, "condition_type": "level_reached", "condition_value": 5},
        {"code": "level_10", "title": "Мастер алгоритмов (Level 10)", "description": "Достичь 10-го уровня", "icon": "shield", "badge_color": "teal", "category": "general", "xp_reward": 500, "condition_type": "level_reached", "condition_value": 10},
    ]
    for ach in achievements_data:
        session.add(Achievement(**ach))

    # 3. Seed Daily Missions
    missions_data = [
        {"title": "Ответить на 10 вопросов ЕНТ", "description": "Пройдите тренировку или тест и ответьте минимум на 10 вопросов", "mission_type": "answer_questions", "target_count": 10, "xp_reward": 60, "icon": "help-circle"},
        {"title": "Решить задачу на Python", "description": "Напишите код и пройдите автоматические тесты в тренажере", "mission_type": "solve_coding", "target_count": 1, "xp_reward": 80, "icon": "code"},
        {"title": "Пройти один урок теории", "description": "Изучите материал любого урока по кодированию, базам данных или сетям", "mission_type": "read_lesson", "target_count": 1, "xp_reward": 40, "icon": "book-open"},
        {"title": "Сдать полноценный квиз", "description": "Завершите тематический квиз или босс-челлендж", "mission_type": "complete_quiz", "target_count": 1, "xp_reward": 50, "icon": "check-square"},
    ]
    for m in missions_data:
        session.add(DailyMission(**m))

    # 4. Seed Course & Curriculum
    course = Course(
        title="ЕНТ Информатика: Полный курс подготовки (50 баллов)",
        slug="unt-informatics-full",
        description="Комплексная программа подготовки к Единому Национальному Тестированию Казахстана по профилю 'Информатика'. Разбор всех спецификаций НЦТ: от систем счисления до архитектуры сетей и SQL.",
        icon="graduation-cap",
        order_index=1,
        is_published=True
    )
    session.add(course)
    await session.flush()

    # Topic 1: Системы счисления и кодирование
    topic1 = Topic(
        course_id=course.id,
        title="Системы счисления и представление информации",
        slug="number-systems-and-coding",
        description="Двоичная, восьмеричная, шестнадцатеричная системы. Перевод между системами, биты/байты, кодирование текста (ASCII, Unicode), растровых и векторных изображений.",
        icon="binary",
        color_accent="sky",
        order_index=1,
        est_minutes=45,
        xp_reward=150
    )
    session.add(topic1)
    await session.flush()

    lesson1_1 = Lesson(
        topic_id=topic1.id,
        title="Позиционные системы счисления: Двоичная, 8-ричная и 16-ричная",
        slug="positional-number-systems",
        content="""# Системы счисления в ЕНТ

Позиционная система счисления — это система, в которой значение каждой цифры определяется её позицией (разрядом) в числе.

### Основные основания:
* **Двоичная (BIN, основание 2)**: цифры `0, 1`
* **Восьмеричная (OCT, основание 8)**: цифры `0, 1, 2, 3, 4, 5, 6, 7`
* **Десятичная (DEC, основание 10)**: цифры `0..9`
* **Шестнадцатеричная (HEX, основание 16)**: `0..9, A(10), B(11), C(12), D(13), E(14), F(15)`

### Быстрый перевод через триады и тетрады:
* 1 восьмеричная цифра = **3 бита** (триада)
* 1 шестнадцатеричная цифра = **4 бита** (тетрада)

```python
# Пример в Python:
x = 0b101101  # 45 в десятичной
hex_val = hex(x) # '0x2d'
oct_val = oct(x) # '0o55'
```
""",
        summary="Правила перевода между двоичной, десятичной и шестнадцатеричной системами счисления для ЕНТ.",
        order_index=1,
        xp_reward=30,
    )
    session.add(lesson1_1)

    lesson1_2 = Lesson(
        topic_id=topic1.id,
        title="Кодирование текста и формулы Хартли/Шеннона",
        slug="text-encoding-hartley",
        content="""# Кодирование информации и формула Хартли

Формула связи мощности алфавита $N$ и веса одного символа $i$ (в битах):
$$N = 2^i$$

### Общий объем текстового сообщения:
$$I = K \\times i$$
где $K$ — количество символов в тексте, $i$ — информационный вес одного символа в битах.

### Стандарты кодировок:
1. **ASCII (8 бит = 1 байт)**: алфавит до $2^8 = 256$ символов.
2. **Unicode (UTF-16, 16 бит = 2 байта)**: алфавит до $2^{16} = 65536$ символов.
3. **UTF-8 (переменная длина от 1 до 4 байт)**: стандарт современного веба.
""",
        summary="Формула Хартли N = 2^i и расчет объема текстовых файлов в байтах и килобайтах.",
        order_index=2,
        xp_reward=30,
    )
    session.add(lesson1_2)

    # Quiz 1
    quiz1 = Quiz(
        topic_id=topic1.id,
        title="Тест: Системы счисления и кодирование данных",
        description="Проверьте свои навыки перевода чисел и расчета информационного объема сообщений по стандартам ЕНТ.",
        quiz_type=QuizType.STANDARD.value,
        time_limit_seconds=420,
        passing_score=70,
        xp_reward=70
    )
    session.add(quiz1)
    await session.flush()

    q1_1 = Question(
        quiz_id=quiz1.id,
        text="Чему равно десятичное число 45 в двоичной системе счисления?",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="easy",
        points=1,
        order_index=1,
        explanation="45 = 32 + 8 + 4 + 1 = 2^5 + 2^3 + 2^2 + 2^0 = 101101₂"
    )
    session.add(q1_1)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=q1_1.id, text="101101", is_correct=True, order_index=1),
        QuestionOption(question_id=q1_1.id, text="110101", is_correct=False, order_index=2),
        QuestionOption(question_id=q1_1.id, text="100111", is_correct=False, order_index=3),
        QuestionOption(question_id=q1_1.id, text="101110", is_correct=False, order_index=4),
    ])

    q1_2 = Question(
        quiz_id=quiz1.id,
        text="Сколько байт займет текст из 1024 символов, закодированный в таблице Unicode (16 бит на символ)?",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="medium",
        points=1,
        order_index=2,
        explanation="16 бит = 2 байта. 1024 символа * 2 байта = 2048 байт (или 2 Кбайт)."
    )
    session.add(q1_2)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=q1_2.id, text="2048 байт", is_correct=True, order_index=1),
        QuestionOption(question_id=q1_2.id, text="1024 байта", is_correct=False, order_index=2),
        QuestionOption(question_id=q1_2.id, text="512 байт", is_correct=False, order_index=3),
        QuestionOption(question_id=q1_2.id, text="4096 байт", is_correct=False, order_index=4),
    ])

    q1_3 = Question(
        quiz_id=quiz1.id,
        text="Переведите шестнадцатеричное число 2F в восьмеричную систему счисления.",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="hard",
        points=2,
        order_index=3,
        explanation="2F₁₆ -> 2=0010, F=1111 -> 00101111₂ -> разбиваем на триады: 000 101 111 -> 0, 5, 7 -> 57₈"
    )
    session.add(q1_3)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=q1_3.id, text="57", is_correct=True, order_index=1),
        QuestionOption(question_id=q1_3.id, text="47", is_correct=False, order_index=2),
        QuestionOption(question_id=q1_3.id, text="67", is_correct=False, order_index=3),
        QuestionOption(question_id=q1_3.id, text="37", is_correct=False, order_index=4),
    ])

    # Topic 2: Базы данных и SQL
    topic2 = Topic(
        course_id=course.id,
        title="Реляционные базы данных и язык SQL",
        slug="relational-databases-and-sql",
        description="Модели данных, первичные и внешние ключи, нормализация (1NF, 2NF, 3NF), типы связей (1:1, 1:N, M:N), операторы SQL (SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY).",
        icon="database",
        color_accent="purple",
        order_index=2,
        est_minutes=60,
        xp_reward=200
    )
    session.add(topic2)
    await session.flush()

    lesson2_1 = Lesson(
        topic_id=topic2.id,
        title="Проектирование БД: Первичные ключи и нормализация",
        slug="db-design-normalization",
        content="""# Реляционные базы данных в ЕНТ

Реляционная база данных представляет собой совокупность связанных таблиц (отношений).

### Ключевые понятия:
1. **Первичный ключ (Primary Key)** — уникальное поле (или набор полей), однозначно идентифицирующее каждую запись в таблице. Не может содержать `NULL`.
2. **Внешний ключ (Foreign Key)** — поле в одной таблице, ссылающееся на первичный ключ другой таблицы для обеспечения ссылочной целостности.

### Нормальные формы:
* **1NF**: Все атрибуты атомарны (неделимы), нет повторяющихся групп.
* **2NF**: Находится в 1NF и каждый неключевой атрибут полностью зависит от всего составного первичного ключа.
* **3NF**: Находится в 2NF и отсутствуют транзитивные зависимости (неключевые атрибуты зависят только от первичного ключа).
""",
        summary="Основные понятия реляционной модели, правила связей 1:N и три нормальные формы.",
        order_index=1,
        xp_reward=30,
    )
    session.add(lesson2_1)

    lesson2_2 = Lesson(
        topic_id=topic2.id,
        title="Язык SQL: Выборка, фильтрация, агрегация и JOIN",
        slug="sql-queries-joins",
        content="""# Запросы SQL для ЕНТ

### Базовая структура SELECT:
```sql
SELECT column1, COUNT(column2)
FROM students
WHERE grade >= 10
GROUP BY column1
HAVING COUNT(column2) > 5
ORDER BY column1 ASC;
```

### Виды объединений (JOIN):
* **INNER JOIN**: возвращает строки, для которых есть совпадение в обеих таблицах.
* **LEFT JOIN**: возвращает все строки из левой таблицы и совпадающие из правой.
* **RIGHT JOIN**: все строки из правой таблицы.
* **FULL OUTER JOIN**: все строки при наличии совпадения хотя бы в одной таблице.
""",
        summary="Синтаксис SQL SELECT, фильтрация WHERE/HAVING, группировка GROUP BY и объединения JOIN.",
        order_index=2,
        xp_reward=30,
    )
    session.add(lesson2_2)

    # Quiz 2
    quiz2 = Quiz(
        topic_id=topic2.id,
        title="Тест: Базы данных и основы SQL",
        description="Тест на знание реляционной алгебры, первичных/внешних ключей и синтаксиса SQL запросов.",
        quiz_type=QuizType.STANDARD.value,
        time_limit_seconds=480,
        passing_score=75,
        xp_reward=80
    )
    session.add(quiz2)
    await session.flush()

    q2_1 = Question(
        quiz_id=quiz2.id,
        text="Какое ключевое слово в SQL используется для исключения дубликатов в результатах запроса?",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="easy",
        points=1,
        order_index=1,
        explanation="Оператор SELECT DISTINCT возвращает только уникальные значения."
    )
    session.add(q2_1)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=q2_1.id, text="DISTINCT", is_correct=True, order_index=1),
        QuestionOption(question_id=q2_1.id, text="UNIQUE", is_correct=False, order_index=2),
        QuestionOption(question_id=q2_1.id, text="GROUP", is_correct=False, order_index=3),
        QuestionOption(question_id=q2_1.id, text="DIFFERENT", is_correct=False, order_index=4),
    ])

    q2_2 = Question(
        quiz_id=quiz2.id,
        text="Какой вид связи образуется между сущностями 'Ученик' и 'Кружок' (если ученик может посещать несколько кружков, а в кружке состоит много учеников)?",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="medium",
        points=1,
        order_index=2,
        explanation="Связь 'Многие-ко-многим' (Many-to-Many, M:N), реализуется через промежуточную связующую таблицу (junction table)."
    )
    session.add(q2_2)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=q2_2.id, text="Многие-ко-многим (M:N)", is_correct=True, order_index=1),
        QuestionOption(question_id=q2_2.id, text="Один-ко-многим (1:N)", is_correct=False, order_index=2),
        QuestionOption(question_id=q2_2.id, text="Один-к-одному (1:1)", is_correct=False, order_index=3),
        QuestionOption(question_id=q2_2.id, text="Древовидная связь", is_correct=False, order_index=4),
    ])

    # Topic 3: Программирование на Python и алгоритмы
    topic3 = Topic(
        course_id=course.id,
        title="Алгоритмизация и программирование на Python",
        slug="python-and-algorithms",
        description="Типы данных, циклы (for, while), срезы строк, методы списков и словарей, базовые алгоритмы поиска и сортировки, рекурсия, обработка файлов.",
        icon="code",
        color_accent="green",
        order_index=3,
        est_minutes=75,
        xp_reward=250
    )
    session.add(topic3)
    await session.flush()

    lesson3_1 = Lesson(
        topic_id=topic3.id,
        title="Срезы строк и списков в Python",
        slug="python-slicing-and-lists",
        content="""# Срезы в Python (Slicing)

Формат среза: `sequence[start:stop:step]`
* `start` — начальный индекс (включительно)
* `stop` — конечный индекс (не включительно)
* `step` — шаг среза

```python
s = "Информатика"
print(s[0:4])   # "Инфо"
print(s[::-1])  # "акитаМрофнИ" (разворот строки)
print(s[::2])   # "Ифрмаиа" (каждый второй символ)
```

### Важные методы списков:
* `append(x)` — добавить в конец ($O(1)$)
* `pop()` — удалить и вернуть последний ($O(1)$)
* `insert(i, x)` — вставка на позицию ($O(n)$)
* `sort()` — быстрая сортировка Timsort ($O(n \\log n)$)
""",
        summary="Полный синтаксис срезов и оценка сложности операций со списками в Python.",
        order_index=1,
        xp_reward=30,
    )
    session.add(lesson3_1)

    # Coding Tasks for Python
    task1 = CodingTask(
        topic_id=topic3.id,
        title="Сумма четных чисел в диапазоне",
        slug="sum-of-even-numbers",
        description="""Напишите программу на Python, которая считывает два целых числа $A$ и $B$ ($A \\le B$) и находит сумму всех **четных** чисел на отрезке от $A$ до $B$ включительно.

### Формат входных данных:
Два целых числа $A$ и $B$, каждое на отдельной строке.

### Формат выходных данных:
Одно целое число — сумма четных чисел.

### Пример:
**Вход:**
`1`
`10`

**Выход:**
`30` (2 + 4 + 6 + 8 + 10 = 30)
""",
        starter_code="""# Считайте числа A и B
a = int(input())
b = int(input())

# Напишите решение здесь
total = 0
for x in range(a, b + 1):
    if x % 2 == 0:
        total += x

print(total)
""",
        solution_code="""a = int(input())
b = int(input())
print(sum(x for x in range(a, b + 1) if x % 2 == 0))
""",
        difficulty="easy",
        time_limit_seconds=1.5,
        memory_limit_mb=50,
        xp_reward=60,
        is_published=True
    )
    session.add(task1)
    await session.flush()

    session.add_all([
        TestCase(task_id=task1.id, input_data="1\n10", expected_output="30", is_hidden=False, order_index=1),
        TestCase(task_id=task1.id, input_data="2\n4", expected_output="6", is_hidden=False, order_index=2),
        TestCase(task_id=task1.id, input_data="1\n1", expected_output="0", is_hidden=True, order_index=3),
        TestCase(task_id=task1.id, input_data="10\n20", expected_output="90", is_hidden=True, order_index=4),
        TestCase(task_id=task1.id, input_data="-4\n4", expected_output="0", is_hidden=True, order_index=5),
    ])

    task2 = CodingTask(
        topic_id=topic3.id,
        title="Палиндром без учета пробелов и регистра",
        slug="palindrome-checker",
        description="""Проверьте, является ли введенная строка палиндромом (читается одинаково слева направо и справа налево), игнорируя пробелы и регистр букв.

### Формат входных данных:
Одна строка текста.

### Формат выходных данных:
Выведите `YES`, если строка является палиндромом, и `NO` в противном случае.

### Пример:
**Вход:**
`А роза упала на лапу Азора`

**Выход:**
`YES`
""",
        starter_code="""text = input()

# Напишите ваш алгоритм проверки
cleaned = text.replace(" ", "").lower()
if cleaned == cleaned[::-1]:
    print("YES")
else:
    print("NO")
""",
        solution_code="""text = input().replace(" ", "").lower()
print("YES" if text == text[::-1] else "NO")
""",
        difficulty="medium",
        time_limit_seconds=1.5,
        memory_limit_mb=50,
        xp_reward=80,
        is_published=True
    )
    session.add(task2)
    await session.flush()

    session.add_all([
        TestCase(task_id=task2.id, input_data="А роза упала на лапу Азора", expected_output="YES", is_hidden=False, order_index=1),
        TestCase(task_id=task2.id, input_data="Kazakhstan", expected_output="NO", is_hidden=False, order_index=2),
        TestCase(task_id=task2.id, input_data="radar", expected_output="YES", is_hidden=True, order_index=3),
        TestCase(task_id=task2.id, input_data="ab c ba", expected_output="YES", is_hidden=True, order_index=4),
        TestCase(task_id=task2.id, input_data="Python", expected_output="NO", is_hidden=True, order_index=5),
    ])

    # Topic 4: Компьютерные сети и безопасность
    topic4 = Topic(
        course_id=course.id,
        title="Компьютерные сети и информационная безопасность",
        slug="networks-and-cybersecurity",
        description="Модель OSI и стек TCP/IP, IP-адресация и маски подсети, DNS, топологии сетей, основы симметричного и асимметричного шифрования, электронная цифровая подпись (ЭЦП).",
        icon="shield",
        color_accent="orange",
        order_index=4,
        est_minutes=50,
        xp_reward=180
    )
    session.add(topic4)
    await session.flush()

    lesson4_1 = Lesson(
        topic_id=topic4.id,
        title="Модель OSI и сетевые протоколы",
        slug="osi-model-protocols",
        content="""# 7 уровней модели OSI

1. **Прикладной (Application)**: HTTP, HTTPS, FTP, SMTP, DNS
2. **Представительский (Presentation)**: SSL/TLS, JPEG, ASCII
3. **Сеансовый (Session)**: RPC, NetBIOS
4. **Транспортный (Transport)**: TCP (надежный с подтверждением), UDP (быстрый без подтверждения)
5. **Сетевой (Network)**: IP, ICMP, маршрутизаторы
6. **Канальный (Data Link)**: Ethernet, MAC-адреса, коммутаторы (свитчи)
7. **Физический (Physical)**: Витая пара, оптоволокно, радиоволны, концентраторы (хабы)
""",
        summary="Разбор всех 7 уровней эталонной модели OSI и протоколов для вопросов ЕНТ.",
        order_index=1,
        xp_reward=30,
    )
    session.add(lesson4_1)

    # UNT Mock Exam Quiz (Grand Boss Challenge)
    boss_quiz = Quiz(
        topic_id=None,
        title="Генеральный Пробный ЕНТ по Информатике (Босс-Челлендж)",
        description="Полноценный симулятор реального экзаменационного тестирования с ограничением по времени и вопросами из всех разделов информатики.",
        quiz_type=QuizType.UNT_MOCK.value,
        time_limit_seconds=1200,
        passing_score=70,
        xp_reward=200,
        is_published=True
    )
    session.add(boss_quiz)
    await session.flush()

    bq1 = Question(
        quiz_id=boss_quiz.id,
        text="Какой протокол транспортного уровня модели OSI гарантирует доставку пакетов и установку соединения?",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="medium",
        points=1,
        order_index=1,
        explanation="TCP (Transmission Control Protocol) обеспечивает надежную доставку с 3-way handshake."
    )
    session.add(bq1)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=bq1.id, text="TCP", is_correct=True, order_index=1),
        QuestionOption(question_id=bq1.id, text="UDP", is_correct=False, order_index=2),
        QuestionOption(question_id=bq1.id, text="IP", is_correct=False, order_index=3),
        QuestionOption(question_id=bq1.id, text="ICMP", is_correct=False, order_index=4),
    ])

    bq2 = Question(
        quiz_id=boss_quiz.id,
        text="Что выведет следующий фрагмент кода на Python?\n\ns = [x ** 2 for x in range(5) if x % 2 != 0]\nprint(sum(s))",
        code_snippet="s = [x ** 2 for x in range(5) if x % 2 != 0]\nprint(sum(s))",
        question_type=QuestionType.SINGLE_CHOICE.value,
        difficulty="medium",
        points=1,
        order_index=2,
        explanation="Нечетные x из range(5): 1 и 3. Квадраты: 1²=1, 3²=9. Сумма: 1 + 9 = 10."
    )
    session.add(bq2)
    await session.flush()
    session.add_all([
        QuestionOption(question_id=bq2.id, text="10", is_correct=True, order_index=1),
        QuestionOption(question_id=bq2.id, text="30", is_correct=False, order_index=2),
        QuestionOption(question_id=bq2.id, text="14", is_correct=False, order_index=3),
        QuestionOption(question_id=bq2.id, text="25", is_correct=False, order_index=4),
    ])

    await session.commit()


async def init_db_data(session: AsyncSession):
    existing_user = await session.execute(select(User).limit(1))
    if not existing_user.scalars().first():
        await _seed_base_data(session)

    # Always seed / update Data Platform components (Sources, Glossary, Specifications, Bank Questions, UNT News)
    from app.db.seed_data_platform import seed_data_platform
    await seed_data_platform(session)
