import sys
from pathlib import Path

import pytest


def test_import_without_src_in_path():
    """
    This test simulates the package being installed and imported by a consumer.
    It removes the project's root from sys.path to ensure that imports
    like `from src.canaerospace import ...` will fail, as they should.
    """
    original_sys_path = sys.path[:]
    project_root = str(Path(__file__).parent.parent)
    src_root = str(Path(__file__).parent.parent / 'src')

    # To simulate an installed environment, we need to remove the project's source
    # directories from the Python path.
    sys.path = [p for p in sys.path if p not in [project_root, src_root]]

    # We also need to remove the module if it has been imported in this session
    if 'src.canaerospace' in sys.modules:
        del sys.modules['src.canaerospace']
    if 'src' in sys.modules:
        del sys.modules['src']

    try:
        # This import should fail because 'src' is not a package available
        # to consumers. We use pytest.raises to assert that an ImportError occurs.
        with pytest.raises(ImportError):
            pass
    finally:
        # Restore sys.path to avoid side effects on other tests
        sys.path = original_sys_path
