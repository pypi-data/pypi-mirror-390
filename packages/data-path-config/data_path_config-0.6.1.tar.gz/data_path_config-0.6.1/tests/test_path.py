import os
import pathlib
import pytest
import shutil
from data_path_config.path import DataPathConfig

@pytest.fixture
def clean_env(monkeypatch):
    # Remove environment variables for isolation (though class doesn't use them)
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("LOG_DIR", raising=False)

def print_green(msg):
    print(f"\033[92m{msg}\033[0m")

def test_data_dir_base(tmp_path, clean_env):
    print_green("Running test_data_dir_base...")
    # Use /tmp/data and /tmp/log for testing
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = DataPathConfig(
        project_name="projA",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject="subA"
    )
    assert pc.data_dir() == data_root.resolve()
    assert pc.project_dir() == (data_root / "projA").resolve()
    assert pc.sub_project_dir() == (data_root / "projA" / "subA").resolve()
    print_green("test_data_dir_base passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_log_dir_base(tmp_path, clean_env):
    print_green("Running test_log_dir_base...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = DataPathConfig(
        project_name="projB",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject="subB"
    )
    assert pc.log_dir() == log_root.resolve()
    assert pc.project_log_dir() == (log_root / "projB").resolve()
    assert pc.sub_project_log_dir() == (log_root / "projB" / "subB").resolve()
    print_green("test_log_dir_base passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_no_subproject_raises(tmp_path, clean_env):
    print_green("Running test_no_subproject_raises...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = DataPathConfig(
        project_name="projC",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject=None
    )
    with pytest.raises(ValueError):
        pc.sub_project_dir()
    with pytest.raises(ValueError):
        pc.sub_project_log_dir()
    print_green("test_no_subproject_raises passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_get_project_today_file_name():
    print_green("Running test_get_project_today_file_name...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = DataPathConfig(
        project_name="projD",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject="subD"
    )
    from datetime import date
    expected = pc.sub_project_dir() / f"projD_subD_{date.today()}.json"
    assert pc.get_project_today_file_name() == expected
    print_green("test_get_project_today_file_name passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)

def test_get_project_today_file_name_no_subproject():
    print_green("Running test_get_project_today_file_name_no_subproject...")
    data_root = pathlib.Path("/tmp/data")
    log_root = pathlib.Path("/tmp/log")
    data_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    pc = DataPathConfig(
        project_name="projE",
        data_dir=str(data_root),
        log_dir=str(log_root),
        subproject=None
    )
    from datetime import date
    expected = pc.project_dir() / f"projE_{date.today()}.json"
    assert pc.get_project_today_file_name() == expected
    print_green("test_get_project_today_file_name_no_subproject passed.")
    # Cleanup
    shutil.rmtree(data_root, ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)
