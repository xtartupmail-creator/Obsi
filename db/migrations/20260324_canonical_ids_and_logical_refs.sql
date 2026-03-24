-- Canonical ID standardization across PostgreSQL and Neo4j logical references.

-- 1) Add canonical IDs (UUIDv4 format) to core tables.
alter table if exists observation
  add column if not exists canonical_id uuid;

alter table if exists infrastructure
  add column if not exists canonical_id uuid;

alter table if exists chain
  add column if not exists canonical_id uuid;

-- Backfill should be performed by application or migration runner that can generate UUIDv4 values.

-- Enforce not null + uniqueness after backfill.
do $$
begin
  if exists (select 1 from information_schema.columns where table_name = 'observation' and column_name = 'canonical_id') then
    execute 'alter table observation alter column canonical_id set not null';
    execute 'create unique index if not exists ux_observation_canonical_id on observation(canonical_id)';
  end if;

  if exists (select 1 from information_schema.columns where table_name = 'infrastructure' and column_name = 'canonical_id') then
    execute 'alter table infrastructure alter column canonical_id set not null';
    execute 'create unique index if not exists ux_infrastructure_canonical_id on infrastructure(canonical_id)';
  end if;

  if exists (select 1 from information_schema.columns where table_name = 'chain' and column_name = 'canonical_id') then
    execute 'alter table chain alter column canonical_id set not null';
    execute 'create unique index if not exists ux_chain_canonical_id on chain(canonical_id)';
  end if;
end
$$;

-- 2) Rename comments to avoid FK wording; use logical-reference semantics.
comment on column observation.graph_observation_canonical_id is
  'logical reference to Neo4j Observation(canonical_id)';

comment on column infrastructure.graph_infrastructure_canonical_id is
  'logical reference to Neo4j Infrastructure(canonical_id)';

comment on column chain.graph_chain_canonical_id is
  'logical reference to Neo4j Chain(canonical_id)';
