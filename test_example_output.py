# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest


def test_passes():
    assert True

def test_fails():
    assert False

@pytest.mark.skip
def test_skip():
    assert True

def test_import_error():
    import doestnotexist
    assert True