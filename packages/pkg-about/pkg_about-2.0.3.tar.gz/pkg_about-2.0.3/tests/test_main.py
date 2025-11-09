# Copyright (c) 2020 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
import sys
import os
import stat
import shutil
from pathlib import Path

from . import test_dir

import pkg_about


class MainTestCase(unittest.TestCase):

    @staticmethod
    def is_namedtuple_instance(obj):
        return (isinstance(obj, tuple) and
                hasattr(obj, '_fields') and
                isinstance(obj._fields, tuple) and
                all(isinstance(field, str) for field in obj._fields))

    @classmethod
    def setUpClass(cls):
        pyproject_path = Path(__file__).resolve().parent.parent/"pyproject.toml"
        if sys.version_info >= (3, 11):
            import tomllib
        else:  # pragma: no cover
            import tomli as tomllib
        with pyproject_path.open("rb") as file:
            metadata = tomllib.load(file).get("project", {})
        cls.version_expected = metadata["version"]
        version_parts = cls.version_expected.split(".")
        cls.version_major_expected = int(version_parts[0])
        cls.version_minor_expected = int(version_parts[1])
        cls.version_micro_expected = int(version_parts[2])

    def test_about(self):
        about = pkg_about.about("pkg_about")
        self.assertIsInstance(about, dict)
        self.assertIs(__title__, about.__title__)
        self.assertEqual(about.__title__, "pkg_about")
        self.assertIs(__version__, about.__version__)
        self.assertEqual(about.__version__, self.version_expected)
        self.assertIs(__version_info__, about.__version_info__)
        self.assertTrue(self.is_namedtuple_instance(about.__version_info__))
        self.assertEqual(about.__version_info__.major, self.version_major_expected)
        self.assertEqual(about.__version_info__.minor, self.version_minor_expected)
        self.assertEqual(about.__version_info__.micro, self.version_micro_expected)
        self.assertEqual(about.__version_info__.releaselevel, "final")
        self.assertEqual(about.__version_info__.serial, 0)
        self.assertIs(__summary__, about.__summary__)
        self.assertEqual(about.__summary__, "Shares Python package metadata at runtime.")
        self.assertIs(__uri__, about.__uri__)
        self.assertEqual(about.__uri__, "https://pypi.org/project/pkg-about/")
        self.assertIs(__author__, about.__author__)
        self.assertEqual(about.__author__, "Adam Karpierz")
        self.assertIs(__email__, about.__email__)
        self.assertEqual(about.__email__, about.__author_email__)
        self.assertIs(__author_email__, about.__author_email__)
        self.assertEqual(about.__author_email__, "Adam Karpierz <adam@karpierz.net>")
        self.assertIs(__maintainer__, about.__maintainer__)
        self.assertEqual(about.__maintainer__, "Adam Karpierz")
        self.assertIs(__maintainer_email__, about.__maintainer_email__)
        self.assertEqual(about.__maintainer_email__, "Adam Karpierz <adam@karpierz.net>")
        self.assertIs(__license__, about.__license__)
        self.assertEqual(about.__license__, "Zlib")
        self.assertIs(__copyright__, about.__copyright__)
        self.assertEqual(about.__copyright__, __author__)

    def test_about_from_setup(self):
        package_path = Path(__file__).resolve().parent.parent
        setup_cfg = shutil.copy(test_dir/"data/setup.cfg", package_path/"setup.cfg")
        try:
            ret_about = pkg_about.about_from_setup(package_path)
            self.assertIs(ret_about, about)
            self.assertIsInstance(about, dict)
            self.assertEqual(about.__title__, "pkg_about")
            self.assertEqual(about.__version__, self.version_expected)
            self.assertTrue(self.is_namedtuple_instance(about.__version_info__))
            self.assertEqual(about.__version_info__.major, self.version_major_expected)
            self.assertEqual(about.__version_info__.minor, self.version_minor_expected)
            self.assertEqual(about.__version_info__.micro, self.version_micro_expected)
            self.assertEqual(about.__version_info__.releaselevel, "final")
            self.assertEqual(about.__version_info__.serial, 0)
            self.assertEqual(about.__summary__, "Shares Python package metadata at runtime.")
            self.assertEqual(about.__uri__, "https://pypi.org/project/pkg-about/")
            self.assertEqual(about.__author__, "Adam Karpierz")
            self.assertEqual(about.__email__, about.__author_email__)
            self.assertEqual(about.__author_email__, "Adam Karpierz <adam@karpierz.net>")
            self.assertEqual(about.__maintainer__, "Adam Karpierz")
            self.assertEqual(about.__maintainer_email__, "Adam Karpierz <adam@karpierz.net>")
            self.assertEqual(about.__license__, "Zlib")
            self.assertEqual(about.__copyright__, about.__author__)
        finally:
            os.chmod(setup_cfg, stat.S_IWRITE)
            setup_cfg.unlink()

    def test_about_appdirs(self):
        about = pkg_about.about("appdirs")
        self.assertIsInstance(about, dict)
        self.assertIs(__title__, about.__title__)
        self.assertEqual(about.__title__, "appdirs")
        self.assertIs(__version__, about.__version__)
        self.assertEqual(about.__version__, "1.4.4")
        self.assertIs(__version_info__, about.__version_info__)
        self.assertTrue(self.is_namedtuple_instance(about.__version_info__))
        self.assertEqual(about.__version_info__.major, 1)
        self.assertEqual(about.__version_info__.minor, 4)
        self.assertEqual(about.__version_info__.micro, 4)
        self.assertEqual(about.__version_info__.releaselevel, "final")
        self.assertEqual(about.__version_info__.serial, 0)
        self.assertIs(__summary__, about.__summary__)
        self.assertEqual(about.__summary__, ('A small Python module for determining appropriate'
                                             ' platform-specific dirs, e.g. a "user data dir".'))
        self.assertIs(__uri__, about.__uri__)
        self.assertEqual(about.__uri__, "http://github.com/ActiveState/appdirs")
        self.assertIs(__author__, about.__author__)
        self.assertEqual(about.__author__, "Trent Mick")
        self.assertIs(__email__, about.__email__)
        self.assertEqual(about.__email__, about.__author_email__)
        self.assertIs(__author_email__, about.__author_email__)
        self.assertEqual(about.__author_email__, "trentm@gmail.com")
        self.assertIs(__maintainer__, about.__maintainer__)
        self.assertEqual(about.__maintainer__, "Jeff Rouse")
        self.assertIs(__maintainer_email__, about.__maintainer_email__)
        self.assertEqual(about.__maintainer_email__, "jr@its.to")
        self.assertIs(__license__, about.__license__)
        self.assertEqual(about.__license__, "MIT")
        self.assertIs(__copyright__, about.__copyright__)
        self.assertEqual(about.__copyright__, __author__)
