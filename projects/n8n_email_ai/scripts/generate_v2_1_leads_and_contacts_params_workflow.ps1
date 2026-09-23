param(
  [string]$LeadSource = 'E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_enriched_v2_1.json',
  [string]$ContactSource = 'E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_lead_contacts_enriched_v2_1.json',
  [string]$OutPath = 'E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_contacts_params_v2_1.json',
  [string]$WorkflowName = 'marketing_db_odata_leads_contacts_params_v2_1'
)

$ErrorActionPreference = 'Stop'

$lead = Get-Content -LiteralPath $LeadSource -Raw -Encoding UTF8 | ConvertFrom-Json
$contact = Get-Content -LiteralPath $ContactSource -Raw -Encoding UTF8 | ConvertFrom-Json

$leadNodes = @{}
foreach ($n in $lead.nodes) { $leadNodes[$n.name] = $n }

$contactNodes = @{}
foreach ($n in $contact.nodes) { $contactNodes[$n.name] = $n }

$wf = [ordered]@{
  name = $WorkflowName
  nodes = @()
  connections = [ordered]@{}
  settings = $lead.settings
  staticData = $null
  pinData = [ordered]@{}
  tags = @(
    @{ name = 'marketing_db' },
    @{ name = '1c-read-only' },
    @{ name = 'v2.1' }
  )
}

# Manual trigger
$mt = $leadNodes['Manual Trigger']
$mt.position = @(240, 260)

# Params (operator-editable for each run)
$params = [ordered]@{
  parameters = @{
    values = @{
      number = @(
        @{ name = 'review_year'; value = 2025 },
        @{ name = 'offset'; value = 0 },
        @{ name = 'limit'; value = 30 },
        @{ name = 'pool_top'; value = 5000 }
      )
    }
  }
  id = 'RunParams'
  name = 'Run params'
  type = 'n8n-nodes-base.set'
  typeVersion = 3
  position = @(420, 260)
}

# Postgres test
$pg = $leadNodes['PostgreSQL test query']
$pg.position = @(660, 260)

# Auxiliary catalogs
$folders = $leadNodes['Fetch lead folders']
$folders.position = @(900, 120)

$tags = $leadNodes['Fetch tags catalog']
$tags.position = @(1140, 120)

# Fetch leads pool (dynamic pool_top)
$fetchLeads = $leadNodes['Fetch leads sample']
$fetchLeads.id = 'FetchLeadsPool'
$fetchLeads.name = 'Fetch leads pool'
$fetchLeads.position = @(1380, 260)
$fetchLeads.parameters.url = '={{ `http://artem.medianasoft.spb.ru/unf/odata/standard.odata/Catalog_%D0%9B%D0%B8%D0%B4%D1%8B?$filter=IsFolder%20eq%20false%20and%20DeletionMark%20eq%20false&$top=${$items(''Run params'', 0, 0)[0].json.pool_top}&$format=json` }}'

# Select by year+offset+limit, output wrapper { value:[rows...] }
$selectByParams = [ordered]@{
  parameters = @{
    jsCode = @'
const params = $json;
const paramsItem = $items('Run params', 0, 0)[0]?.json || {};
const payload = $json;
const rows = Array.isArray(payload?.value) ? payload.value : [];

const reviewYear = Number(paramsItem.review_year);
const offset = Math.max(0, Number(paramsItem.offset) || 0);
const limit = Math.max(0, Number(paramsItem.limit) || 0);

const createdDateKey = '\u0414\u0430\u0442\u0430\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u044f';

const parseCreatedDate = (row) => {
  const raw = row[createdDateKey];
  if (typeof raw === 'string' && raw && !raw.startsWith('0001-01-01')) {
    const d = new Date(raw);
    if (!Number.isNaN(d.getTime())) return { date: d, source: createdDateKey };
  }

  const ref = typeof row.Ref_Key === 'string' ? row.Ref_Key.trim() : '';
  const parts = ref.split('-');
  if (parts.length !== 5) return { date: null, source: null };

  try {
    const timeLow = BigInt('0x' + parts[0]);
    const timeMid = BigInt('0x' + parts[1]);
    const timeHiAndVersion = BigInt('0x' + parts[2]);
    const version = Number((timeHiAndVersion >> 12n) & 0xfn);
    if (version !== 1) return { date: null, source: null };

    const timeHi = timeHiAndVersion & 0x0fffn;
    const uuidTimestamp100ns = (timeHi << 48n) | (timeMid << 32n) | timeLow;
    const unixEpoch100ns = 122192928000000000n;
    const unix100ns = uuidTimestamp100ns - unixEpoch100ns;
    const ms = Number(unix100ns / 10000n);
    const d = new Date(ms);
    if (Number.isNaN(d.getTime())) return { date: null, source: null };
    return { date: d, source: 'Ref_Key UUIDv1' };
  } catch {
    return { date: null, source: null };
  }
};

const candidates = rows
  .filter((row) => !row.IsFolder && !row.DeletionMark)
  .map((row) => {
    const created = parseCreatedDate(row);
    return {
      ...row,
      __review_created_at: created.date ? created.date.toISOString() : null,
      __review_created_year: created.date ? created.date.getUTCFullYear() : null,
      __review_created_source: created.source,
    };
  })
  .filter((row) => row.__review_created_year === reviewYear)
  .sort((a, b) => String(b.__review_created_at || '').localeCompare(String(a.__review_created_at || '')));

const selected = candidates.slice(offset, offset + limit);

return [{
  json: {
    value: selected,
    review_year: reviewYear,
    offset,
    limit,
    source_rows: rows.length,
    year_rows: candidates.length,
    selected_count: selected.length,
  }
}];
'@
  }
  id = 'SelectByParams'
  name = 'Select leads by year+offset'
  type = 'n8n-nodes-base.code'
  typeVersion = 2
  position = @(1620, 260)
}

# Explode wrapper.value into items
# NOTE: We intentionally do NOT explode here. The downstream `Normalize owner` code node
# expects an object shaped like `{ value: [...] }` and produces per-owner items itself.

# Normalize owner (uses folders/tags via $items)
$normOwner = $leadNodes['Normalize owner']
$normOwner.position = @(1860, 260)

# IF/Upsert owners (rename IF to avoid conflict later)
$ifOwner = $leadNodes['IF skipped=false']
$ifOwner.id = 'IfOwnerNotSkipped'
$ifOwner.name = 'IF owner skipped=false'
$ifOwner.position = @(2100, 260)

$upsertOwner = $leadNodes['Upsert onec_owners']
$upsertOwner.position = @(2340, 260)

# Fetch contacts for each owner row
$fetchContacts = $contactNodes['Fetch lead contacts sample']
$fetchContacts.id = 'FetchLeadContactsForOwner'
$fetchContacts.name = 'Fetch lead contacts for owner'
$fetchContacts.position = @(2580, 260)
$fetchContacts.parameters.url = '={{ `http://artem.medianasoft.spb.ru/unf/odata/standard.odata/Catalog_%D0%9A%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82%D1%8B%D0%9B%D0%B8%D0%B4%D0%BE%D0%B2?$filter=Owner_Key%20eq%20guid''${$json.owner_ref_key}''&$top=200&$format=json` }}'

$normContact = $contactNodes['Normalize contact']
$normContact.position = @(2820, 260)

$ifContact = $contactNodes['IF skipped=false']
$ifContact.id = 'IfContactNotSkipped'
$ifContact.name = 'IF contact skipped=false'
$ifContact.position = @(3060, 260)

$upsertContact = $contactNodes['Upsert onec_contacts']
$upsertContact.position = @(3300, 260)

$wf.nodes = @(
  $mt,
  $params,
  $pg,
  $folders,
  $tags,
  $fetchLeads,
  $selectByParams,
  $normOwner,
  $ifOwner,
  $upsertOwner,
  $fetchContacts,
  $normContact,
  $ifContact,
  $upsertContact
)

function New-MainConnection($NodeName) {
  $inner = @([ordered]@{ node = $NodeName; type = 'main'; index = 0 })
  $outer = ,$inner
  return [ordered]@{ main = $outer }
}

# Connections (linear, plus folders/tags branch as in original lead workflow)
$wf.connections['Manual Trigger'] = New-MainConnection 'Run params'
$wf.connections['Run params'] = New-MainConnection 'PostgreSQL test query'
$wf.connections['PostgreSQL test query'] = New-MainConnection 'Fetch lead folders'
$wf.connections['Fetch lead folders'] = New-MainConnection 'Fetch tags catalog'
$wf.connections['Fetch tags catalog'] = New-MainConnection 'Fetch leads pool'
$wf.connections['Fetch leads pool'] = New-MainConnection 'Select leads by year+offset'
$wf.connections['Select leads by year+offset'] = New-MainConnection 'Normalize owner'
$wf.connections['Normalize owner'] = New-MainConnection 'IF owner skipped=false'
$wf.connections['IF owner skipped=false'] = New-MainConnection 'Upsert onec_owners'
$wf.connections['Upsert onec_owners'] = New-MainConnection 'Fetch lead contacts for owner'
$wf.connections['Fetch lead contacts for owner'] = New-MainConnection 'Normalize contact'
$wf.connections['Normalize contact'] = New-MainConnection 'IF contact skipped=false'
$wf.connections['IF contact skipped=false'] = New-MainConnection 'Upsert onec_contacts'

$jsonText = $wf | ConvertTo-Json -Depth 100
[IO.File]::WriteAllText($OutPath, $jsonText, (New-Object System.Text.UTF8Encoding($false)))
Write-Output $OutPath
