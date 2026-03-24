create index if not exists idx_chain_nodes_chain_step on chain_nodes(chain_id, step_number);
create index if not exists idx_findings_asset_created on agent_findings(asset_id, created_at desc);
create index if not exists idx_findings_chain_tags on agent_findings using gin(chain_tags);
create index if not exists idx_findings_vector_tags on agent_findings using gin(attack_vector_tags);

create or replace function arr_overlap_score(a text[], b text[])
returns double precision language sql immutable as $$
  with
    i as (select count(*)::float c from (select unnest(a) intersect select unnest(b)) t),
    u as (select count(*)::float c from (select unnest(a) union select unnest(b)) t)
  select case when (select c from u)=0 then 0 else (select c from i)/(select c from u) end;
$$;

create or replace view vw_chain_candidates as
select
  rc.chain_id,
  rc.tenant_id,
  rc.chain_status,
  cn.finding_id as last_finding_id,
  af.asset_id,
  af.chain_tags as last_chain_tags,
  af.attack_vector_tags as last_vector_tags,
  af.created_at as last_created_at
from risk_chains rc
join lateral (
  select cn2.*
  from chain_nodes cn2
  where cn2.chain_id = rc.chain_id
  order by cn2.step_number desc
  limit 1
) cn on true
join agent_findings af on af.finding_id = cn.finding_id;

create or replace function chain_append(
  p_tenant_id uuid,
  p_chain_id uuid,
  p_finding_id uuid
) returns void language plpgsql as $$
declare
  next_step int;
begin
  select coalesce(max(step_number),0)+1 into next_step
  from chain_nodes where chain_id = p_chain_id;

  insert into chain_nodes(node_id, tenant_id, chain_id, finding_id, step_number)
  values (gen_random_uuid(), p_tenant_id, p_chain_id, p_finding_id, next_step);

  update risk_chains
     set step_count = step_count + 1,
         updated_at = now()
   where chain_id = p_chain_id;
end;
$$;

create or replace function chain_merge(
  p_tenant_id uuid,
  p_chain_a uuid,
  p_chain_b uuid
) returns uuid language plpgsql as $$
declare
  base_step int;
begin
  if p_chain_a = p_chain_b then
    return p_chain_a;
  end if;

  select coalesce(max(step_number),0) into base_step
  from chain_nodes where chain_id = p_chain_a;

  with moved as (
    select node_id, row_number() over(order by step_number) rn
    from chain_nodes where chain_id = p_chain_b
  )
  update chain_nodes cn
     set chain_id = p_chain_a,
         step_number = base_step + m.rn
    from moved m
   where cn.node_id = m.node_id;

  update risk_chains
     set step_count = (select count(*) from chain_nodes where chain_id = p_chain_a),
         updated_at = now()
   where chain_id = p_chain_a;

  delete from risk_chains where chain_id = p_chain_b;

  return p_chain_a;
end;
$$;

create or replace function chain_rescore(
  p_chain_id uuid,
  p_objective double precision,
  p_exploitability double precision,
  p_blast double precision,
  p_detection double precision,
  p_completeness double precision
) returns double precision language plpgsql as $$
declare
  s double precision;
  st text;
begin
  s := (0.35*p_objective) + (0.25*p_exploitability) + (0.20*p_blast) + (0.10*p_detection) + (0.10*p_completeness);
  st := case
    when s >= 0.70 then 'CRITICAL'
    when s >= 0.50 then 'VALIDATED'
    when s >= 0.30 then 'CANDIDATE'
    else 'POTENTIAL'
  end;

  update risk_chains
     set chain_score = s,
         chain_status = st,
         updated_at = now()
   where chain_id = p_chain_id;

  return s;
end;
$$;
