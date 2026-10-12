import pytest
from dbt.tests.util import run_dbt

from dbt.adapters.polars.testing.mixin import PolarsTestMixin

_MODEL = """
{{ config(materialized='table') }}
SELECT 1 AS id UNION ALL SELECT 2 AS id
"""

# run-operation does not populate the adapter cache, so the ref() below has no
# registered node config. It must still resolve, the way `dbt run` resolves it.
_MACRO = """
{% macro count_ids() %}
  {% set r = run_query("SELECT COUNT(*) AS n FROM " ~ ref('ids')) %}
  {% if r.rows[0][0] != 2 %}
    {{ exceptions.raise_compiler_error("expected 2 rows, got " ~ r.rows[0][0]) }}
  {% endif %}
{% endmacro %}
"""


class TestRunOperationRef(PolarsTestMixin):
    @pytest.fixture(scope="class")
    def models(self):
        return {"ids.sql": _MODEL}

    @pytest.fixture(scope="class")
    def macros(self):
        return {"count_ids.sql": _MACRO}

    def test_run_operation_reads_a_ref(self, project):
        run_dbt(["run"])
        run_dbt(["run-operation", "count_ids"])
