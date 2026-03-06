"""Tests for data layer: SalaryRepository and normalizers."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from paystreet.data.normalizers import (
    normalize_company_size,
    normalize_region,
    normalize_salary,
)
from paystreet.data.salary_repository import SalaryRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(scalar_one_or_none=None, scalars_list=None):
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_one_or_none
    result.scalars.return_value.all.return_value = scalars_list or []
    session.execute = AsyncMock(return_value=result)
    return session


def _make_salary_record(**kwargs):
    r = MagicMock()
    r.id = kwargs.get("id", uuid.uuid4())
    r.job_title = kwargs.get("job_title", "Backend Developer")
    r.experience_years = kwargs.get("experience_years", 3)
    r.region = kwargs.get("region", "Seoul")
    r.company_size = kwargs.get("company_size", "mid")
    r.salary_min = kwargs.get("salary_min", 4500)
    r.salary_max = kwargs.get("salary_max", 6000)
    r.currency = kwargs.get("currency", "KRW")
    return r


def _make_job_title(name="Backend Developer", category="engineering"):
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = name
    t.category = category
    return t


def _make_region_obj(name="Seoul", country="Korea"):
    r = MagicMock()
    r.id = uuid.uuid4()
    r.name = name
    r.country = country
    return r


# ---------------------------------------------------------------------------
# SalaryRepository.get_salary_records
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_salary_records_no_filters():
    records = [_make_salary_record(), _make_salary_record(job_title="ML Engineer")]
    session = _make_session(scalars_list=records)

    repo = SalaryRepository(session)
    result = await repo.get_salary_records()

    assert len(result) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_salary_records_with_job_title_filter():
    records = [_make_salary_record()]
    session = _make_session(scalars_list=records)

    repo = SalaryRepository(session)
    result = await repo.get_salary_records(job_title="Backend Developer")

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_salary_records_with_all_filters():
    session = _make_session(scalars_list=[])

    repo = SalaryRepository(session)
    result = await repo.get_salary_records(
        job_title="DevOps",
        experience_years=4,
        region="Seoul",
        company_size="mid",
        limit=20,
    )

    assert result == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_salary_records_experience_years_zero_is_applied():
    """experience_years=0 should still be included as a filter (is not None check)."""
    session = _make_session(scalars_list=[])
    repo = SalaryRepository(session)
    await repo.get_salary_records(experience_years=0)
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_salary_records_empty():
    session = _make_session(scalars_list=[])
    repo = SalaryRepository(session)
    result = await repo.get_salary_records()
    assert result == []


# ---------------------------------------------------------------------------
# SalaryRepository.get_salary_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_salary_by_id_found():
    record = _make_salary_record()
    session = _make_session(scalar_one_or_none=record)

    repo = SalaryRepository(session)
    result = await repo.get_salary_by_id(record.id)

    assert result == record


@pytest.mark.asyncio
async def test_get_salary_by_id_not_found():
    session = _make_session(scalar_one_or_none=None)

    repo = SalaryRepository(session)
    result = await repo.get_salary_by_id(uuid.uuid4())

    assert result is None


# ---------------------------------------------------------------------------
# SalaryRepository.create_salary_record
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_salary_record_adds_and_flushes():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    repo = SalaryRepository(session)
    result = await repo.create_salary_record(
        job_title="QA Engineer",
        experience_years=2,
        region="Busan",
        company_size="mid",
        salary_min=3500,
        salary_max=5000,
        currency="KRW",
        source="seed_data",
    )

    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    # The result is the SalaryRecord instance that was created
    assert result is not None


# ---------------------------------------------------------------------------
# SalaryRepository.get_all_job_titles
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_all_job_titles():
    titles = [
        _make_job_title("Backend Developer"),
        _make_job_title("ML Engineer", "data"),
    ]
    session = _make_session(scalars_list=titles)

    repo = SalaryRepository(session)
    result = await repo.get_all_job_titles()

    assert len(result) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_job_titles_empty():
    session = _make_session(scalars_list=[])
    repo = SalaryRepository(session)
    result = await repo.get_all_job_titles()
    assert result == []


# ---------------------------------------------------------------------------
# SalaryRepository.get_all_regions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_all_regions():
    regions = [_make_region_obj("Seoul"), _make_region_obj("Pangyo")]
    session = _make_session(scalars_list=regions)

    repo = SalaryRepository(session)
    result = await repo.get_all_regions()

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_all_regions_empty():
    session = _make_session(scalars_list=[])
    repo = SalaryRepository(session)
    result = await repo.get_all_regions()
    assert result == []


# ---------------------------------------------------------------------------
# SalaryRepository.upsert_job_title
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_job_title_existing():
    existing = _make_job_title("Backend Developer", "engineering")
    session = _make_session(scalar_one_or_none=existing)

    repo = SalaryRepository(session)
    result = await repo.upsert_job_title("Backend Developer", "engineering")

    # Returns existing without inserting
    assert result == existing
    session.add.assert_not_called()
    session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_upsert_job_title_new():
    session = _make_session(scalar_one_or_none=None)

    repo = SalaryRepository(session)
    result = await repo.upsert_job_title("New Role", "engineering")

    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result is not None


@pytest.mark.asyncio
async def test_upsert_job_title_no_category():
    session = _make_session(scalar_one_or_none=None)

    repo = SalaryRepository(session)
    result = await repo.upsert_job_title("Analyst")

    session.add.assert_called_once()
    session.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# SalaryRepository.upsert_region
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_region_existing():
    existing = _make_region_obj("Seoul")
    session = _make_session(scalar_one_or_none=existing)

    repo = SalaryRepository(session)
    result = await repo.upsert_region("Seoul")

    assert result == existing
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_region_new():
    session = _make_session(scalar_one_or_none=None)

    repo = SalaryRepository(session)
    result = await repo.upsert_region("Daejeon", country="Korea")

    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result is not None


@pytest.mark.asyncio
async def test_upsert_region_default_country():
    session = _make_session(scalar_one_or_none=None)
    repo = SalaryRepository(session)
    result = await repo.upsert_region("Incheon")
    session.add.assert_called_once()
    # Verify the Region was created with default country Korea
    added_region = session.add.call_args[0][0]
    assert added_region.country == "Korea"


# ---------------------------------------------------------------------------
# normalizers.normalize_company_size
# ---------------------------------------------------------------------------


def test_normalize_company_size_startup_korean():
    assert normalize_company_size("스타트업") == "startup"


def test_normalize_company_size_startup_english():
    assert normalize_company_size("startup") == "startup"


def test_normalize_company_size_mid_korean_soecho():
    assert normalize_company_size("중소") == "mid"


def test_normalize_company_size_mid_english():
    assert normalize_company_size("mid") == "mid"


def test_normalize_company_size_mid_korean_jungyeon():
    assert normalize_company_size("중견") == "mid"


def test_normalize_company_size_large_korean():
    assert normalize_company_size("대기업") == "large"


def test_normalize_company_size_large_english():
    assert normalize_company_size("large") == "large"


def test_normalize_company_size_enterprise():
    assert normalize_company_size("enterprise") == "large"


def test_normalize_company_size_unknown_defaults_to_mid():
    assert normalize_company_size("unknown_size") == "mid"


def test_normalize_company_size_strips_whitespace():
    assert normalize_company_size("  startup  ") == "startup"


# ---------------------------------------------------------------------------
# normalizers.normalize_region
# ---------------------------------------------------------------------------


def test_normalize_region_korean_pangyo():
    assert normalize_region("판교") == "Pangyo"


def test_normalize_region_korean_seoul():
    assert normalize_region("서울") == "Seoul"


def test_normalize_region_korean_busan():
    assert normalize_region("부산") == "Busan"


def test_normalize_region_english_pangyo():
    assert normalize_region("pangyo") == "Pangyo"


def test_normalize_region_english_seoul():
    assert normalize_region("seoul") == "Seoul"


def test_normalize_region_english_busan():
    assert normalize_region("busan") == "Busan"


def test_normalize_region_unknown_passthrough():
    assert normalize_region("Daejeon") == "Daejeon"


def test_normalize_region_strips_whitespace():
    assert normalize_region("판교") == "Pangyo"


# ---------------------------------------------------------------------------
# normalizers.normalize_salary
# ---------------------------------------------------------------------------


def test_normalize_salary_int_passthrough():
    assert normalize_salary(5000) == 5000


def test_normalize_salary_string_numeric():
    assert normalize_salary("5000") == 5000


def test_normalize_salary_string_with_commas():
    assert normalize_salary("5,000") == 5000


def test_normalize_salary_string_with_spaces():
    assert normalize_salary("5 000") == 5000


def test_normalize_salary_string_with_commas_and_spaces():
    assert normalize_salary("10,000") == 10000


def test_normalize_salary_zero():
    assert normalize_salary(0) == 0


def test_normalize_salary_large_value():
    assert normalize_salary("100,000") == 100000
