In general, SSAS objects can be changed in the SSAS database with their standard methods:

- create
- update
- delete
- rename
- refresh

!!! note SSAS Methods

    Not all objects have all methods and some have none since they are read-only.


However, there can be cases where individually calling each method makes the overall process unreasonably slow. To improve this speed, you can use the `Batch` class to combine multiple changes into a single query

# Example

```python
from pbi_core import LocalReport
from pbi_core.ssas.server.batch import Batch

ssas_report = LocalReport.load_pbix("example_pbis/api.pbix")
drop_cmds = (
    [t.delete_cmd() for t in ssas_report.ssas.tables]
    + [r.delete_cmd() for r in ssas_report.ssas.relationships]
    + [tp.delete_cmd() for tp in ssas_report.ssas.table_permissions]
)
batch_command = Batch(commands=drop_cmds).render_xml()
ssas_report.ssas.server.query_xml(batch_command)
```

The output should look like 

```shell
2025-10-31 11:56:33 [info     ] Loading PBIX report            load_ssas=True load_static_files=True path=example_pbis/test_ssas.pbix
2025-10-31 11:56:33 [info     ] Loading PBIX SSAS              path=example_pbis/test_ssas.pbix
2025-10-31 11:56:33 [info     ] Re-using existing local SSAS instance port=61419
2025-10-31 11:56:33 [info     ] Tabular Model load complete   
2025-10-31 11:56:33 [info     ] Syncing from SSAS              db_name=test_ssas
2025-10-31 11:56:33 [info     ] Loading PBIX Static Files      path=example_pbis/test_ssas.pbix
2025-10-31 11:56:33 [info     ] Loaded PBIX report             components=ssas+static
2025-10-31 11:56:33 [info     ] Preparing Batch Command for SSAS delete={'table': 8, 'relationship': 1, 'table_permission': 1}
```

!!! warn Differences with method calls

    In the delete method of certain classes - such as variations, relationships and partitions - contain additional checks to drop dependent objects to ensure that the query resolves as expected. The delete_cmd method does not contain this logic, so you can get errors running `Batch(commands=[partition.delete_cmd()])` when `partition_delete()` succeeds.