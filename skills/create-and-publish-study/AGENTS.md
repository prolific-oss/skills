# Create and Publish Study

**Version 0.0.1**  
Prolific  
March 2026

> **Note:**  
> This document is for AI agents and LLMs to follow when working with  
> CLI skill for creating and publishing Prolific research studies. Humans may also find it useful,  
> but guidance here is optimized for automation and consistency.  

---

## Abstract

Prolific CLI guide for creating and publishing research studies using the prolific CLI tool. Covers YAML-driven study configuration, study creation, and publishing workflows for AI research pipelines.

---

## Table of Contents

2. [Study Creation](#2-study-creation) - **HIGH**
   - 2.1 [Ethical Reward Calculation](#21-ethical-reward-calculation)

---

## 2. Study Creation

**Impact: HIGH**

Rules for building valid study configurations, including required fields and ethical constraints.

### 2.1 Ethical Reward Calculation

**Impact: HIGH**

Prolific requires a minimum of £6.00 / $8.00 per hour. The recommended rate is £9.00 / $12.00 per hour. Reward is set in **pence** (GBP) or **cents** (USD) and is fixed once a study is published — it can be increased but never reduced.

Formula: `reward_pence = round((hourly_rate_pence × estimated_minutes) / 60)`

Quick reference at the recommended £9.00/hr rate: 5 min → `75p`, 10 min → `150p`, 15 min → `225p`, 30 min → `450p`.

**Underpaying: Wrong**

```yaml
estimated_completion_time: 10
reward: 50
```

£0.50 for 10 min = £3.00/hr — below Prolific's minimum of £6.00/hr. Prolific will flag this as underpaying.

**Minimum compliant: Acceptable**

```yaml
estimated_completion_time: 10
reward: 100
```

£1.00 for 10 min = £6.00/hr — meets Prolific's minimum threshold.

**Recommended rate: Good**

```yaml
estimated_completion_time: 10
reward: 150
```

£1.50 for 10 min = £9.00/hr — Prolific's recommended ethical rate.

---

## References

1. [https://docs.prolific.com/documentation/tooling/prolific-cli.md](https://docs.prolific.com/documentation/tooling/prolific-cli.md)
2. [https://github.com/prolific-oss/cli](https://github.com/prolific-oss/cli)
