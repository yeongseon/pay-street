"""Tests for infrastructure modules: database, logging_config, main lifespan, seed_data."""

import logging
import uuid
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# logging_config
# ---------------------------------------------------------------------------


def test_setup_logging_configures_root_logger():
    from paystreet.app.logging_config import setup_logging

    mock_settings = MagicMock()
    mock_settings.log_level = "INFO"

    with patch("paystreet.app.logging_config.get_settings", return_value=mock_settings):
        setup_logging()

    root_logger = logging.getLogger()
    assert root_logger.level <= logging.INFO


def test_setup_logging_debug_level():
    from paystreet.app.logging_config import setup_logging

    mock_settings = MagicMock()
    mock_settings.log_level = "DEBUG"

    with patch("paystreet.app.logging_config.get_settings", return_value=mock_settings):
        setup_logging()

    root_logger = logging.getLogger()
    assert root_logger.level <= logging.DEBUG


def test_setup_logging_quiets_noisy_loggers():
    from paystreet.app.logging_config import setup_logging

    mock_settings = MagicMock()
    mock_settings.log_level = "INFO"

    with patch("paystreet.app.logging_config.get_settings", return_value=mock_settings):
        setup_logging()

    assert logging.getLogger("sqlalchemy.engine").level == logging.WARNING
    assert logging.getLogger("httpx").level == logging.WARNING


def test_get_logger_returns_named_logger():
    from paystreet.app.logging_config import get_logger

    logger = get_logger("paystreet.test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "paystreet.test"


def test_get_logger_different_names():
    from paystreet.app.logging_config import get_logger

    l1 = get_logger("module.a")
    l2 = get_logger("module.b")
    assert l1.name != l2.name


# ---------------------------------------------------------------------------
# database
# ---------------------------------------------------------------------------


def test_get_engine_creates_engine():
    import paystreet.app.database as db_module

    # Reset global state
    original_engine = db_module._engine
    db_module._engine = None

    mock_settings = MagicMock()
    mock_settings.database_url = "postgresql+asyncpg://test:test@localhost/testdb"
    mock_settings.debug = False

    with patch("paystreet.app.database.get_settings", return_value=mock_settings):
        with patch("paystreet.app.database.create_async_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            engine = db_module.get_engine()

    assert engine == mock_engine
    mock_create.assert_called_once()

    # Restore
    db_module._engine = original_engine


def test_get_engine_singleton():
    import paystreet.app.database as db_module

    original_engine = db_module._engine
    db_module._engine = None

    mock_settings = MagicMock()
    mock_settings.database_url = "postgresql+asyncpg://test:test@localhost/testdb"
    mock_settings.debug = False

    with patch("paystreet.app.database.get_settings", return_value=mock_settings):
        with patch("paystreet.app.database.create_async_engine") as mock_create:
            mock_create.return_value = MagicMock()
            e1 = db_module.get_engine()
            e2 = db_module.get_engine()

    assert e1 is e2
    assert mock_create.call_count == 1

    db_module._engine = original_engine


def test_get_session_factory_creates_factory():
    import paystreet.app.database as db_module

    original_factory = db_module._session_factory
    db_module._session_factory = None

    mock_engine = MagicMock()

    with patch("paystreet.app.database.get_engine", return_value=mock_engine):
        with patch("paystreet.app.database.async_sessionmaker") as mock_maker:
            mock_maker.return_value = MagicMock()
            factory = db_module.get_session_factory()

    assert factory is not None
    mock_maker.assert_called_once()

    db_module._session_factory = original_factory


def test_get_session_factory_singleton():
    import paystreet.app.database as db_module

    original_factory = db_module._session_factory
    db_module._session_factory = None

    mock_engine = MagicMock()

    with patch("paystreet.app.database.get_engine", return_value=mock_engine):
        with patch("paystreet.app.database.async_sessionmaker") as mock_maker:
            mock_maker.return_value = MagicMock()
            f1 = db_module.get_session_factory()
            f2 = db_module.get_session_factory()

    assert f1 is f2
    assert mock_maker.call_count == 1

    db_module._session_factory = original_factory


@pytest.mark.asyncio
async def test_close_db_disposes_engine():
    import paystreet.app.database as db_module

    original_engine = db_module._engine
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()
    db_module._engine = mock_engine

    await db_module.close_db()

    mock_engine.dispose.assert_awaited_once()
    assert db_module._engine is None

    db_module._engine = original_engine


@pytest.mark.asyncio
async def test_close_db_noop_when_no_engine():
    import paystreet.app.database as db_module

    original_engine = db_module._engine
    db_module._engine = None

    # Should not raise
    await db_module.close_db()

    db_module._engine = original_engine


@pytest.mark.asyncio
async def test_init_db_creates_tables():
    import paystreet.app.database as db_module

    mock_conn = AsyncMock()
    mock_engine = MagicMock()

    class FakeCM:
        async def __aenter__(self):
            return mock_conn

        async def __aexit__(self, *args):
            pass

    mock_engine.begin = MagicMock(return_value=FakeCM())

    with patch("paystreet.app.database.get_engine", return_value=mock_engine):
        with patch("paystreet.app.database.Base") as MockBase:
            MockBase.metadata.create_all = MagicMock()
            await db_module.init_db()

    mock_conn.run_sync.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_yields_session():
    import paystreet.app.database as db_module

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    mock_factory = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_cm

    with patch("paystreet.app.database.get_session_factory", return_value=mock_factory):
        async for session in db_module.get_db():
            assert session == mock_session


@pytest.mark.asyncio
async def test_get_db_rollback_on_exception():
    import paystreet.app.database as db_module

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock(side_effect=RuntimeError("commit failed"))
    mock_session.rollback = AsyncMock()

    mock_factory = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_cm

    with patch("paystreet.app.database.get_session_factory", return_value=mock_factory):
        with pytest.raises(RuntimeError, match="commit failed"):
            async for session in db_module.get_db():
                pass  # commit raises inside the generator


# ---------------------------------------------------------------------------
# main.py lifespan
# ---------------------------------------------------------------------------


def test_app_has_correct_title():
    from paystreet.app.main import app

    assert app.title == "PayStreet API"
    assert app.version == "0.1.0"


def test_app_routers_registered():
    from paystreet.app.main import app

    routes = {r.path for r in app.routes}
    assert "/health" in routes
    assert any("/api/v1/salary" in r for r in routes)
    assert any("/api/v1/topics" in r for r in routes)
    assert any("/api/v1/scripts" in r for r in routes)
    assert any("/api/v1/pipeline" in r for r in routes)
    assert any("/api/v1/admin" in r for r in routes)


def test_app_cors_middleware():
    from paystreet.app.main import app
    from fastapi.middleware.cors import CORSMiddleware

    middleware_types = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_types


@pytest.mark.asyncio
async def test_lifespan_calls_init_and_close():
    from paystreet.app.main import lifespan
    from fastapi import FastAPI

    with (
        patch("paystreet.app.main.init_db") as mock_init,
        patch("paystreet.app.main.close_db") as mock_close,
        patch("paystreet.app.main.setup_logging"),
    ):
        mock_init.return_value = None
        mock_close.return_value = None

        test_app = FastAPI()
        async with lifespan(test_app):
            mock_init.assert_called_once()

        mock_close.assert_called_once()


# ---------------------------------------------------------------------------
# seed_data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seed_data_seed_function_calls_repo_methods():
    from paystreet.scripts.seed_data import seed, SEED_SALARY_DATA, SEED_REGIONS

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.upsert_region = AsyncMock(return_value=MagicMock())
    mock_repo.upsert_job_title = AsyncMock(return_value=MagicMock())
    mock_repo.create_salary_record = AsyncMock(return_value=MagicMock())

    with patch("paystreet.scripts.seed_data.SalaryRepository", return_value=mock_repo):
        await seed(mock_session)

    assert mock_repo.upsert_region.await_count == len(SEED_REGIONS)
    assert mock_repo.upsert_job_title.await_count > 0
    assert mock_repo.create_salary_record.await_count == len(SEED_SALARY_DATA)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_seed_data_seeds_all_salary_records():
    from paystreet.scripts.seed_data import seed, SEED_SALARY_DATA

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.upsert_region = AsyncMock(return_value=MagicMock())
    mock_repo.upsert_job_title = AsyncMock(return_value=MagicMock())
    mock_repo.create_salary_record = AsyncMock(return_value=MagicMock())

    with patch("paystreet.scripts.seed_data.SalaryRepository", return_value=mock_repo):
        await seed(mock_session)

    assert mock_repo.create_salary_record.await_count == 16  # 16 seed records


@pytest.mark.asyncio
async def test_seed_data_seeds_correct_regions():
    from paystreet.scripts.seed_data import seed

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.upsert_region = AsyncMock(return_value=MagicMock())
    mock_repo.upsert_job_title = AsyncMock(return_value=MagicMock())
    mock_repo.create_salary_record = AsyncMock(return_value=MagicMock())

    with patch("paystreet.scripts.seed_data.SalaryRepository", return_value=mock_repo):
        await seed(mock_session)

    region_calls = [c.kwargs["name"] for c in mock_repo.upsert_region.call_args_list]
    assert "Seoul" in region_calls
    assert "Pangyo" in region_calls
    assert "Busan" in region_calls


@pytest.mark.asyncio
async def test_seed_data_upserts_unique_job_titles():
    from paystreet.scripts.seed_data import seed, SEED_SALARY_DATA

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.upsert_region = AsyncMock(return_value=MagicMock())
    mock_repo.upsert_job_title = AsyncMock(return_value=MagicMock())
    mock_repo.create_salary_record = AsyncMock(return_value=MagicMock())

    with patch("paystreet.scripts.seed_data.SalaryRepository", return_value=mock_repo):
        await seed(mock_session)

    unique_titles = set(row[0] for row in SEED_SALARY_DATA)
    assert mock_repo.upsert_job_title.await_count == len(unique_titles)


def test_seed_data_constants():
    from paystreet.scripts.seed_data import (
        SEED_SALARY_DATA,
        SEED_REGIONS,
        JOB_TITLE_CATEGORIES,
    )

    assert len(SEED_SALARY_DATA) == 16
    assert len(SEED_REGIONS) == 3
    assert "Backend Developer" in JOB_TITLE_CATEGORIES
    assert JOB_TITLE_CATEGORIES["Backend Developer"] == "engineering"
