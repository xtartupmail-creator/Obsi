create extension if not exists "pgcrypto";

create table assets (
  asset_id uuid primary key,
  tenant_id uuid not null,
  fqdn text,
  ip_address inet,
  criticality int not null default 3,
  created_at timestamptz default now()
);

create table agent_findings (
  finding_id uuid primary key,
  tenant_id uuid not null,
  run_id uuid,
  agent_id varchar(32) not null,
  asset_id uuid not null references assets(asset_id),
  finding_type text not null,
  severity text not null,
  confidence double precision not null check (confidence between 0 and 1),
  status text not null default 'new',
  technique_ids text[] not null default '{}',
  tactic_phase text,
  chain_tags text[] not null default '{}',
  attack_vector_tags text[] not null default '{}',
  next_probe_hints jsonb not null default '[]'::jsonb,
  raw_evidence jsonb not null default '{}'::jsonb,
  created_at timestamptz not null
);

create table risk_chains (
  chain_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  chain_score double precision not null default 0,
  chain_status text not null default 'POTENTIAL',
  step_count int not null default 0,
  updated_at timestamptz not null default now()
);

create table chain_nodes (
  node_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  chain_id uuid not null references risk_chains(chain_id) on delete cascade,
  finding_id uuid not null references agent_findings(finding_id) on delete cascade,
  step_number int not null
);

create table finding_links (
  link_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  source_id uuid not null references agent_findings(finding_id),
  target_id uuid not null references agent_findings(finding_id),
  link_type text not null,
  confidence double precision not null,
  link_reason text,
  created_at timestamptz not null default now()
);
