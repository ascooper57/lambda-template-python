# -*- coding: utf-8 -*-

from api.rdb.utils.helpers import get_os_temp_dir, remove_subdir, make_temp_subdir


# noinspection PyUnresolvedReferences
def test_make_temp_subdir():
    import os
    import platform
    import time

    tempdir = get_os_temp_dir()
    if platform.system() == 'Darwin':
        assert tempdir == '/tmp'

    current_milli_time = int(round(time.time() * 1000))
    subdir = str(current_milli_time)
    temp_subdir = make_temp_subdir(subdir)
    assert len(tempdir) < len(temp_subdir)
    assert len(temp_subdir) == len(tempdir) + 1 + len(subdir)
    assert os.path.exists(temp_subdir)
    remove_subdir(temp_subdir)
    assert not os.path.exists(temp_subdir)
