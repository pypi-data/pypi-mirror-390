# -*- coding: utf-8 -*-
"""
OceanBase dialect for cx_oceanbase driver.
"""

from .cx_oracle import OceanBaseDialect_cx_oracle
import cx_Oceanbase


class OceanBaseDialect_cx_oceanbase(OceanBaseDialect_cx_oracle):
    """
    OceanBase dialect for cx_oceanbase driver.
    """

    name = "oceanbase"
    driver = "cx_oceanbase"

    # SQLAlchemy 2.x compatibility
    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls):
        """SQLAlchemy 2.x recommended method name"""
        return cx_Oceanbase

    @classmethod
    def dbapi(cls):
        """Maintain backward compatibility"""
        return cx_Oceanbase


# Register dialect, similar to SQLAlchemy's cx_oracle.py
dialect = OceanBaseDialect_cx_oceanbase
