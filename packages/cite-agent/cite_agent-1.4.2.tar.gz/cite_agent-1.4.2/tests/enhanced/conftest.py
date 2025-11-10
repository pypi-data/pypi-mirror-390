import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def configure_archive_dir(tmp_path_factory):
    archive_root = tmp_path_factory.mktemp("archive_store")
    os.environ["CITE_AGENT_ARCHIVE_DIR"] = str(archive_root)
    return archive_root
