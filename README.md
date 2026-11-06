# Order Automation: Product Case Study

The product side of [order-to-erp-agent](https://github.com/sidd-24/order-to-erp-agent), an LLM agent that turns customer order e-mails into ERP orders. The agent is built and evaluated. This repository covers the questions that come before and after: who it's for, what success means, what it's worth, and how to roll it out without booking a single wrong order.

| Document | Content |
|---|---|
| **[PRD](PRD.md)** | Problem, users, goals and non-goals, prioritised requirements, success metrics, rollout plan, risks, roadmap, open questions |
| **[Business case](business_case.xlsx)** | Cost/benefit model in Excel: every result is a formula over an assumptions sheet, plus a sensitivity table |

## Key points

- **The guardrail comes first.** The metric that decides go or no-go is "wrong orders booked without a person", and its target is zero. The prototype met it on all 93 test documents. Every other metric is optimised only while that one stays at zero.
- **The value is in pre-filling, not in full automation.** In the base case, the model gives EUR 88.8k net benefit a year, 1.8 FTE of capacity and an 8-month payback. Running in assisted mode only, where a person approves every pre-filled order, still keeps about three quarters of that. So the rollout starts there, and auto-approval is earned customer by customer.
- **Phased rollout with exit criteria:** shadow mode on real mail, then assisted mode, then auto-approval for ten customers below EUR 2,000, then general auto-approval. A kill switch falls back to assisted mode at any time.
- **German context in the risk plan:**
  - GDPR, with a data processing agreement for the LLM provider;
  - early works council involvement, since an approval audit log counts as a monitoring system under §87(1) no. 6 BetrVG.

![Business case results](docs/results.png)

## Rebuilding the business case

```bash
pip install openpyxl
python business_case.py            # writes business_case.xlsx
```

The yellow cells on the Inputs sheet are assumptions, each with its source. Change them in Excel and the Results and Sensitivity sheets recalculate.

## Limitations

- **Assumed business inputs.** The order volume, time per order and labour cost are assumptions, not measured figures. The model shows how the result depends on them; the pilot would replace them with real values.
- **Synthetic test set.** The prototype metrics come from 93 synthetic test documents, so they show the design works, not how it will do on real mail.
