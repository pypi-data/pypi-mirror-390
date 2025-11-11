from dvt.context.manifest import ManifestContext
from dvt.contracts.graph.manifest import Manifest

from dbt.adapters.contracts.connection import AdapterRequiredConfig


class QueryHeaderContext(ManifestContext):
    def __init__(self, config: AdapterRequiredConfig, manifest: Manifest) -> None:
        super().__init__(config, manifest, config.project_name)


def generate_query_header_context(config: AdapterRequiredConfig, manifest: Manifest):
    ctx = QueryHeaderContext(config, manifest)
    return ctx.to_dict()
