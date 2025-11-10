"""
DVT adapter management extensions.

This module extends dbt's adapter system to support multi-profile
source connections and compute layer integration.
"""

from dvt.adapters.multi_adapter_manager import (
    MultiAdapterManager,
    create_multi_adapter_manager,
)

__all__ = [
    "MultiAdapterManager",
    "create_multi_adapter_manager",
]
