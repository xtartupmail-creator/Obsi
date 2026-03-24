package correlation.ingest

default allow = false

allow if {
  input.tenant_id != ""
  input.confidence >= 0
  input.confidence <= 1
  count(input.chain_tags) > 0
}

deny[msg] if {
  input.environment == "prod"
  input.finding_type == "anomaly"
  input.confidence < 0.2
  msg := "low-confidence anomaly blocked in prod"
}
