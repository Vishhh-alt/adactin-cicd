# Adactin Hotel — CI/CD Performance Test Repository
## JMeter Bootcamp

---

## Files

```
adactin-cicd/
├── Jenkinsfile                          ← Jenkins pipeline (Part 1)
├── .github/workflows/perf-test.yml     ← GitHub Actions workflow (Part 2)
├── azure-pipelines.yml                 ← Azure DevOps pipeline (Part 2)
├── jmx/
│   └── adactin_booking.jmx             ← JMeter test plan
├── data/
│   └── adactin-credentials.csv         ← login credentials
├── scripts/
│   ├── check_p95.py                    ← P95 gate (all platforms)
│   └── check_trend.py                  ← trend gate (Part 3)
└── results/                            ← gitignored
```

---

## Platform Quick Setup

### Jenkins
1. Install Performance Plugin
2. New Item → Pipeline → Pipeline script from SCM
3. Update JMETER_HOME in Jenkinsfile

### GitHub Actions
1. Push .github/workflows/perf-test.yml
2. Add SLACK_BOT_TOKEN to repository secrets
3. Workflow runs automatically on push

### Azure DevOps
1. Pipelines → New Pipeline → Existing YAML → azure-pipelines.yml
2. Add TEAMS_WEBHOOK_URL as secret pipeline variable
3. Pipeline runs automatically on push

---

## Thresholds

| Threshold | Value | Action |
|---|---|---|
| Error rate | > 0.5% | FAIL |
| Error rate | > 0.1% | UNSTABLE |
| P95 vs last build | > 20% | FAIL |
| P95 absolute | > 3000ms | FAIL |
| 5-build drift | > 15% | FAIL |

---

## Instructor: Visvashwarr Venugopal
## Sr. Technical Lead — Performance Engineering
