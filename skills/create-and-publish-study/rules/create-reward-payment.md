---
name: reward-and-payment
description: Ethical reward calculation and payment guidelines for Prolific studies
---

# Ethical Reward Calculation

**Impact: HIGH**

Prolific requires a minimum of £6.00 / $8.00 per hour. The recommended rate is £9.00 / $12.00 per hour. Reward is set in **pence** (GBP) or **cents** (USD) and is fixed once a study is published — it can be increased but never reduced.

Formula: `reward_pence = round((hourly_rate_pence × estimated_minutes) / 60)`

Quick reference at the recommended £9.00/hr rate: 5 min → `75p`, 10 min → `150p`, 15 min → `225p`, 30 min → `450p`.

### Underpaying (Wrong)

```yaml
estimated_completion_time: 10
reward: 50
```

£0.50 for 10 min = £3.00/hr — below Prolific's minimum of £6.00/hr. Prolific will flag this as underpaying.

### Minimum compliant (Acceptable)

```yaml
estimated_completion_time: 10
reward: 100
```

£1.00 for 10 min = £6.00/hr — meets Prolific's minimum threshold.

### Recommended rate (Good)

```yaml
estimated_completion_time: 10
reward: 150
```

£1.50 for 10 min = £9.00/hr — Prolific's recommended ethical rate.
