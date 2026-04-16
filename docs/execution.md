# Execution

## Order Types

| Type | When to use |
|---|---|
| market | Momentum signals, time-sensitive entries |
| limit | Mean reversion entries at target price |
| vwap | Large fills in liquid names |
| twap | Reducing large positions without excessive impact |

## Venue Scoring

The execution router scores each configured venue before routing:

```
score = (1 / spread) * fill_quality_weight
      + (1 / latency_ms) * latency_weight
      + depth_score * depth_weight
```

Weights are configurable in `config/default.yaml` under `execution.venue_weights`.

## VWAP Algorithm

Child orders are sized proportional to historical volume distribution
across the trading session (9:30–16:00 ET). Participation rate is capped
at 15% of expected volume per interval.

## Error Handling

On order rejection or timeout, the router:
1. Logs the failure with full context
2. Cancels any related open orders on other venues
3. Emits an alert via `AlertManager`
4. Does not retry automatically — retries require explicit strategy logic
