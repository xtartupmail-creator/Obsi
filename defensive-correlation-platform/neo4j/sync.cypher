MERGE (a:Asset {id: $asset_id})
ON CREATE SET a.created_at = datetime($created_at)
SET a.fqdn = $fqdn, a.ip = $ip, a.tenant_id = $tenant_id;

MERGE (f:Finding {id: $finding_id})
ON CREATE SET f.created_at = datetime($created_at)
SET f.tenant_id = $tenant_id,
    f.agent_id = $agent_id,
    f.severity = $severity,
    f.confidence = $confidence,
    f.finding_type = $finding_type,
    f.chain_tags = $chain_tags,
    f.vector_tags = $attack_vector_tags;

MERGE (a)-[:EXPOSED_BY]->(f);

MERGE (c:RiskChain {id: $chain_id})
SET c.tenant_id = $tenant_id,
    c.chain_score = $chain_score,
    c.chain_status = $chain_status,
    c.updated_at = datetime($updated_at);

MERGE (f)-[m:MEMBER_OF]->(c)
SET m.step_number = $step_number;

MATCH (f1:Finding {id: $source_id}), (f2:Finding {id: $target_id})
MERGE (f1)-[e:ENABLES]->(f2)
SET e.confidence = $link_confidence, e.reason = $link_reason;
