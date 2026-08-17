select source, entity, cursor_kind, cursor_value, updated_at
from ingestion_cursors
where source = 'ingestion'
  and entity = 'Catalog_Лиды'
order by cursor_kind;

