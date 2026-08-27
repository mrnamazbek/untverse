# Contributing to UNTverse

Thank you for your interest in contributing to **UNTverse**! We welcome contributions to help Kazakhstan students prepare for the UNT Informatics exam.

---

## 1. Development Workflow

1. Fork the repository and create a new feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Set up the local development environment according to the [Local Development Guide](README.md#local-development).
3. Ensure all tests pass before opening a Pull Request:
   ```bash
   # Run backend tests
   cd backend
   pytest tests/ -v

   # Run frontend build and typecheck
   cd ../frontend
   npm run build
   ```

---

## 2. Branch Naming Conventions

Use clear, descriptive branch prefixes:
- `feat/` — New features (e.g., `feat/sql-playground`, `feat/daily-quests`)
- `fix/` — Bug fixes (e.g., `fix/quiz-timer-expired`, `fix/ast-open-blocking`)
- `refactor/` — Code structural improvements without changing behavior
- `docs/` — Documentation updates
- `chore/` — Dependency upgrades and build tooling

---

## 3. Commit Message Guidelines

We adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <subject>
```

### Examples
- `feat(quiz): add instant question explanation modal`
- `fix(sandbox): prevent memory leak on long stdout capture`
- `docs(readme): add deployment topology diagram`
- `refactor(auth): separate refresh token repository logic`

---

## 4. Code Standards

- **Python & FastAPI**:
  - Follow PEP 8 and use type annotations everywhere.
  - Keep domain services decoupled from database models using repository patterns.
  - Never execute arbitrary Python inside the main API process without AST security verification (`SecurityCheckVisitor`).
- **Next.js & TypeScript**:
  - Follow ESLint rules and TypeScript strict mode.
  - Adhere to the design system tokens defined in `DESIGN-notion.md` (warm canvas `#f6f5f4`, `#0075de` Notion blue, `#213183` indigo night band, Inter typography).

---

## 5. Submitting a Pull Request

1. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
2. Ensure CI checks pass on GitHub Actions.
3. Request review from maintainers.
