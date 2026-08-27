import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_current_unt_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/unt/current")
    assert resp.status_code == 200
    data = resp.json()

    assert data["exam_year"] == 2026
    assert data["is_active"] is True
    assert data["structure"]["total_questions"] == 120
    assert data["structure"]["maximum_score"] == 140
    assert data["structure"]["duration_minutes"] == 240
    assert data["structure"]["passing_threshold_total"] == 50
    assert data["structure"]["passing_threshold_per_subject"] == 5

    # Check informatics specifics
    assert data["informatics_specifics"]["questions_count"] == 50
    assert data["informatics_specifics"]["max_score"] == 50

    # Check profile combinations
    assert "IT_and_CS" in data["profile_combinations"]
    assert "Математика + Информатика" in data["profile_combinations"]["IT_and_CS"]["pair_name_kk"]

    # Check periods and deadlines
    assert len(data["testing_periods"]) == 4
    assert "grant_application_start" in data["important_deadlines"]
    assert len(data["official_source_urls"]) > 0


@pytest.mark.asyncio
async def test_specifications_taxonomy_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/unt/specifications?locale=kk")
    assert resp.status_code == 200
    specs = resp.json()
    assert len(specs) > 0

    spec = specs[0]
    assert spec["exam_year"] == 2026
    assert spec["status"] == "active"
    assert len(spec["sections"]) == 6  # 6 core Informatics sections

    # Check sections
    section_codes = [s["code"] for s in spec["sections"]]
    assert "CS-1" in section_codes
    assert "CS-4" in section_codes  # Python Algorithms
    assert "CS-5" in section_codes  # SQL

    # Check topics inside CS-4
    cs4 = next(s for s in spec["sections"] if s["code"] == "CS-4")
    assert len(cs4["topics"]) >= 5
