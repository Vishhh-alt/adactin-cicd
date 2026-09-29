# CI/CD FOR JMETER — MASTER SCRIPT
## Part 1: Jenkins | Part 2: GitHub Actions & Azure DevOps | Part 3: Advanced Patterns
### Ready-to-Read Script — 100 Minutes

**App: Adactin Hotel (adactinhotelapp.com)**

---

> "Quotes" = speak word for word.
> [BRACKETS] = stage directions, never read aloud.

---

## TIMING GUIDE

| Part | Block | Time | Topic |
|------|-------|------|-------|
| **PART 1** | Why CI/CD for performance | 0:00–8:00 | The problem, the cost, the solution |
| | How Jenkins + JMeter fit together | 8:00–15:00 | Architecture |
| | Install Performance Plugin | 15:00–20:00 | One-time setup |
| | The Jenkinsfile — line by line | 20:00–35:00 | Every stage explained |
| | Hands-on lab — Jenkins | 35:00–45:00 | Trigger builds, introduce regression |
| **PART 2** | GitHub Actions intro | 45:00–50:00 | Why GA, how it differs from Jenkins |
| | GitHub Actions workflow — line by line | 50:00–63:00 | Every step explained |
| | Azure DevOps intro | 63:00–67:00 | YAML pipeline structure |
| | Azure DevOps pipeline — line by line | 67:00–78:00 | Every task explained |
| | Hands-on lab — GA and Azure | 78:00–85:00 | Push, watch pipeline |
| **PART 3** | Parallel execution | 85:00–90:00 | Run tests in parallel jobs |
| | Environment-based thresholds | 90:00–94:00 | Dev vs staging vs prod SLAs |
| | Trend gating | 94:00–97:00 | Block drift before it becomes critical |
| | Notification patterns | 97:00–100:00 | Slack, email, Teams |

---

---

# PART 1 — JENKINS PIPELINE INTEGRATION (0:00–45:00)

---

## BLOCK 1 — WHY CI/CD FOR PERFORMANCE (0:00–8:00)

[No tools open. Talk first.]

"Before we touch Jenkins or any tool — I want to spend eight minutes on why this matters. Because if you understand the why, the how is easy.

---

**The old model — and why it fails.**

In most organisations, performance testing happens once. At the end of the project. Two weeks before go-live. A QA engineer runs a load test, the system is three times slower than the SLA, and the team spends the next two weeks in a panic trying to fix six months of accumulated performance debt.

I have seen this on every project I have worked on until we fixed the process. John Lewis. Oracle implementations. Every single one.

---

**Here is what actually happens on a real project.**

Sprint 1: Adactin Hotel, Search Hotels endpoint, 200ms. Well within SLA.

Sprint 6: a developer adds a hotel star rating filter. They join a new ratings table to the search query. Search Hotels is now 380ms. Nobody notices because nobody tested it.

Sprint 12: another developer adds a photo gallery to hotel listings. The images load via a subquery instead of a JOIN. Search Hotels is now 750ms. Nobody tests it.

Sprint 18: a third developer refactors session validation. Sessions are now re-validated on every request instead of being cached. Search Hotels is now 2.1 seconds. SLA is 3 seconds. Still no alarm.

Sprint 24: go-live preparation. First load test ever. Search Hotels at 200 concurrent users: 14 seconds. Test fails. Go-live postponed by six weeks.

---

The regression happened in Sprint 6. We found it in Sprint 24. Eighteen sprints of debt.

The cost to fix it in Sprint 6: two hours. The developer who wrote the query is still in the code. The change is isolated. A quick fix.

The cost to fix it in Sprint 24: six weeks of go-live delay, emergency triage across three teams, overtime, client relationship damage.

---

**The CI/CD performance testing model.**

CI/CD performance testing runs JMeter automatically on every build. When Sprint 6's ratings join is merged, the pipeline runs the test in 3 minutes, finds 380ms, compares it to the Sprint 5 baseline of 200ms, flags it as a 90% increase, and fails the build. The developer who wrote the query gets the notification within 30 minutes.

The trend does not accumulate. Each sprint starts clean.

---

**Three things CI/CD performance testing gives you:**

One: early detection. Regressions caught in the same sprint they are introduced.

Two: traceability. Every build is linked to the commit that triggered it. You can see exactly which code change caused which performance change.

Three: confidence. When the pipeline is green, you know the build performs within SLA. Not because someone ran a manual test last month — because the automated gate ran 20 minutes ago.

---

This is the professional standard. It is what every enterprise performance engineering team does. Today you learn to build it."

---

## BLOCK 2 — HOW JENKINS AND JMETER FIT TOGETHER (8:00–15:00)

[Draw or show a diagram on screen.]

"Jenkins is a CI/CD automation server. It runs pipelines — sequences of steps that execute automatically on every push to Git.

Here is the architecture for Adactin Hotel:

```
Developer pushes code to Git
        ↓
Jenkins detects the push (webhook or 1-minute poll)
        ↓
Pipeline starts automatically
        ↓
Stage 1: Checkout    — pull JMX, scripts, data files from Git
Stage 2: Perf Test   — run JMeter in Non-GUI mode against Adactin
Stage 3: Gate        — check P95 against SLA, exit 1 if breached
Stage 4: Publish     — archive JTL, publish HTML report, plot trend
        ↓
Gate passes → build GREEN → code is promoted
Gate fails  → build RED   → developer notified, promotion blocked
```

---

Three components work together:

**Jenkins** — the orchestrator. Reads the Jenkinsfile, executes each stage in order, collects results, sends notifications.

**JMeter in Non-GUI mode** — exactly the command from Session 16. Jenkins calls it as a shell command. No GUI. No listeners rendering. Full CPU goes to generating load.

**Jenkins Performance Plugin** — reads the JTL after JMeter finishes. Parses every row. Calculates P95 and error rate per sampler. Compares against thresholds. Fails the build if breached. Plots a trend chart across all builds.

---

The key insight: JMeter is a command-line tool. Jenkins runs command-line tools. The integration is a shell command — that is all. The Performance Plugin adds the intelligence layer on top: trend analysis, threshold enforcement, visual reporting.

---

**What the pipeline does NOT need:**

A JMeter GUI running somewhere. A human watching the test. A manual step to generate the HTML report. All of that is automated."

---

## BLOCK 3 — INSTALL JENKINS PERFORMANCE PLUGIN (15:00–20:00)

[Open Jenkins in browser.]

"One-time setup. Takes two minutes.

Jenkins → Manage Jenkins → Plugins → Available Plugins tab → search: **Performance** → tick **Performance Plugin** → Install → restart Jenkins.

After restart: when you create a post-build action in a pipeline, you will have access to `perfReport()`. That is the function that reads your JTL and plots trends.

---

Also confirm JMeter is installed on your Jenkins agent:

```bash
/opt/apache-jmeter-5.6.3/bin/jmeter -version
```

If this fails — JMeter is not on the agent. Either install it there or use a Docker-based agent that has JMeter in the image. For this session, we assume JMeter is installed at `/opt/apache-jmeter-5.6.3`.

---

That is all the setup. One plugin. One tool on the agent. Everything else is the Jenkinsfile."

---

## BLOCK 4 — THE JENKINSFILE LINE BY LINE (20:00–35:00)

[Open a text editor. Type the Jenkinsfile as you explain it.]

"The Jenkinsfile lives in the root of your performance test repository alongside your JMX files, data files, and scripts. Jenkins reads it automatically when you point a Pipeline job at the repository.

This is Pipeline as Code. The performance gate is version-controlled alongside the test plan. When someone changes the SLA threshold, there is a commit, a code review, an approval. No undocumented changes.

---

```groovy
pipeline {
    agent any
```

`pipeline` — this is a declarative Jenkins pipeline.
`agent any` — run on any available Jenkins agent. In production: `agent { label 'perf-agent' }` to target a specific machine with JMeter installed.

---

```groovy
    environment {
        ADACTIN_HOST  = 'adactinhotelapp.com'
        ADACTIN_PORT  = '443'
        ADACTIN_PROTO = 'https'
        JMETER_HOME   = '/opt/apache-jmeter-5.6.3'
        THREADS       = '5'
        RAMPUP        = '10'
        DURATION      = '120'
        P95_SLA       = '3000'
    }
```

All configurable values in one block at the top. Host, port, protocol, threads, duration, SLA threshold.

In a real project you would have multiple environments — dev, staging, production-like. You parameterise the pipeline and pass different values per environment. The JMX never changes. The command-line arguments change.

`THREADS = '5'` — five users for a CI pipeline. This is not a full load test. It is a regression check. Five users for two minutes gives us stable P95 readings in under three minutes total. The pipeline finishes in five minutes including checkout and publish. Fast enough to run on every commit.

---

```groovy
    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }
```

Pull the latest JMX and scripts from Git. `scm` means whatever source control is configured for this Jenkins job. Every run uses the latest version of the test plan — not a stale copy.

Your repository structure:

```
adactin-perf/
├── Jenkinsfile
├── jmx/
│   └── adactin_booking.jmx
├── data/
│   └── adactin-credentials.csv
└── scripts/
    └── check_p95.py
```

---

```groovy
        stage('Performance Test') {
            steps {
                sh '''
                    mkdir -p results

                    ${JMETER_HOME}/bin/jmeter \
                        -n \
                        -t  jmx/adactin_booking.jmx \
                        -Jhost=${ADACTIN_HOST} \
                        -Jport=${ADACTIN_PORT} \
                        -Jprotocol=${ADACTIN_PROTO} \
                        -Jthreads=${THREADS} \
                        -Jrampup=${RAMPUP} \
                        -Jduration=${DURATION} \
                        -l  results/adactin_${BUILD_NUMBER}.jtl \
                        -e  -o results/report_${BUILD_NUMBER} \
                        -Jjmeter.save.saveservice.print_field_names=true \
                        -Jjmeter.save.saveservice.data_type=false \
                        -Jjmeter.save.saveservice.sent_bytes=false \
                        -Jjmeter.save.saveservice.idle_time=false \
                        -Jjmeter.save.saveservice.connect_time=false
                '''
            }
        }
```

The JMeter command. Non-GUI mode. Every parameter passed as a `-J` flag. The JMX reads them with `${__P(threads,5)}`.

`${BUILD_NUMBER}` — Jenkins built-in. Build 1, build 2, build 3. JTL and report folder named per build. Full history of every run. You can compare report_1 vs report_15 side by side.

The save service properties ensure the JTL has the correct column headers — the fix we applied in Session 16 is baked into the pipeline permanently.

---

```groovy
        stage('Performance Gate') {
            steps {
                sh '''
                    python3 scripts/check_p95.py \
                        results/adactin_${BUILD_NUMBER}.jtl \
                        ${P95_SLA}
                '''
            }
        }
```

The gate. After JMeter finishes, a Python script reads the JTL. If P95 exceeds the SLA, the script exits with code 1. Jenkins treats exit code 1 as stage failure. Build is marked red. Promotion is blocked.

The `check_p95.py` script:

```python
import sys, csv

def check_p95(jtl_file, sla_ms):
    times = []
    with open(jtl_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('success','').strip().lower() == 'true':
                try:
                    times.append(int(row['elapsed']))
                except: continue

    if not times:
        print('ERROR: No successful samples'); sys.exit(1)

    times.sort()
    p95 = times[int(len(times) * 0.95)]

    print(f'Total: {len(times)} | P95: {p95}ms | SLA: {sla_ms}ms')

    if p95 > sla_ms:
        print(f'GATE FAILED — P95 {p95}ms exceeds SLA {sla_ms}ms')
        sys.exit(1)
    print('GATE PASSED')
    sys.exit(0)

if __name__ == '__main__':
    check_p95(sys.argv[1], int(sys.argv[2]))
```

Simple, transparent, extensible. You can add error rate checks, throughput checks, per-sampler P95 checks — any metric in the JTL.

---

```groovy
    post {
        always {
            perfReport(
                sourceDataFiles:                 'results/adactin_${BUILD_NUMBER}.jtl',
                errorFailedThreshold:            0.5,
                errorUnstableThreshold:          0.1,
                relativeFailedThresholdPositive: 20
            )
            publishHTML(target: [
                keepAll: true,
                reportDir:   "results/report_${BUILD_NUMBER}",
                reportFiles: 'index.html',
                reportName:  "JMeter Report Build ${BUILD_NUMBER}"
            ])
            archiveArtifacts artifacts: 'results/*.jtl', fingerprint: true
        }
        failure {
            mail to: 'team@company.com',
                 subject: "PERF FAIL — Build ${BUILD_NUMBER}",
                 body: "Gate failed. See: ${BUILD_URL}"
        }
    }
}
```

`post` runs after all stages — always.

`perfReport` — the Performance Plugin:
- `errorFailedThreshold: 0.5` — build fails if error rate exceeds 0.5%
- `errorUnstableThreshold: 0.1` — build is unstable if error rate exceeds 0.1%
- `relativeFailedThresholdPositive: 20` — build fails if P95 increases more than 20% vs the previous build

`publishHTML` — the full JMeter HTML Dashboard is accessible directly in Jenkins. Click the link on any build to open the report for that specific run.

`archiveArtifacts` — every JTL is saved as a Jenkins artifact. Downloadable. Reprocessable. Permanent history.

`mail` on failure — immediate notification. In production, add a Slack notification too — we cover that in Part 3."

---

## BLOCK 5 — HANDS-ON LAB: JENKINS (35:00–45:00)

[Jenkins open. Repository with Jenkinsfile ready.]

"Four steps. Follow them in order.

---

**Step 1 — Create the Jenkins job.**

Jenkins → New Item → name: `adactin-perf` → Pipeline → OK.

Pipeline section → Definition: Pipeline script from SCM → SCM: Git → Repository URL: your repo → Branch: main → Script Path: Jenkinsfile → Save.

---

**Step 2 — Trigger build 1.**

Click Build Now. Watch the pipeline view — four stages in order.

In the console log find the check_p95.py output:

```
Total: 142 | P95: 520ms | SLA: 3000ms
GATE PASSED
```

Build 1 is green. Click JMeter Report Build 1 — the HTML Dashboard opens in Jenkins.

---

**Step 3 — Trigger build 2.**

No changes. Same result. Trend chart now shows two points — flat line. Performance is stable.

---

**Step 4 — Simulate a regression.**

In the Jenkinsfile change:

```groovy
P95_SLA = '300'
```

Push the change. Trigger build 3.

Console log:

```
Total: 148 | P95: 520ms | SLA: 300ms
GATE FAILED — P95 520ms exceeds SLA 300ms
```

Build 3 is red. Email fires. Trend chart shows the spike.

Reset P95_SLA to 3000. Push. Build 4 is green. The trend chart shows:

```
Build 1: ✅  Build 2: ✅  Build 3: ❌  Build 4: ✅
```

Full regression cycle — detect, fail, fix, recover — completed in under 10 minutes. In production this runs on every commit, automatically."

---

---

# PART 2 — GITHUB ACTIONS & AZURE DEVOPS (45:00–85:00)

---

## BLOCK 6 — GITHUB ACTIONS INTRO (45:00–50:00)

"Jenkins is a self-hosted CI server. You install it, maintain it, patch it, scale it. That is appropriate for enterprises with dedicated infrastructure teams.

GitHub Actions is different. It is CI/CD built into GitHub itself. No installation. No maintenance. No dedicated server. You push code to GitHub — GitHub runs the pipeline on its own infrastructure. For open-source projects it is free. For private repositories, a generous free tier covers most teams.

---

Three key differences from Jenkins:

**One — everything is a YAML file in `.github/workflows/`.** No GUI configuration. No plugin manager. Just a file in your repository.

**Two — runners instead of agents.** GitHub provides cloud-hosted runners — virtual machines with Ubuntu, Windows, or Mac. You can also self-host a runner on your own machine for free.

**Three — the marketplace.** GitHub Actions has a marketplace with thousands of pre-built actions. Installing a plugin in Jenkins requires browsing the plugin manager. In GitHub Actions, you use a pre-built action with one line: `uses: action-name@v1`.

---

For JMeter specifically: there is a dedicated GitHub Action — `QAInsights/jmeter-action`. One line installs JMeter on the runner and runs your test. No manual JMeter installation on the runner required.

---

When to choose GitHub Actions over Jenkins:

Your code is already on GitHub. Your team is small to medium. You want zero infrastructure to maintain. CI/CD pipelines run less than 2000 minutes per month on the free tier.

When to keep Jenkins:

You have complex on-premise infrastructure. You run against internal apps that are not publicly accessible. You need fine-grained control over the agent environment. Your pipelines run thousands of minutes per month."

---

## BLOCK 7 — GITHUB ACTIONS WORKFLOW LINE BY LINE (50:00–63:00)

[Open `.github/workflows/perf-test.yml` in a text editor.]

"The workflow file lives at `.github/workflows/perf-test.yml` in your repository. GitHub detects it automatically.

Here is the complete workflow for Adactin Hotel:

---

```yaml
name: Adactin Performance Test
```

The display name shown in the GitHub Actions UI under the Actions tab.

---

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
```

**Triggers** — when this workflow runs:

`push` to main or develop — runs on every commit to these branches.
`pull_request` to main — runs when a PR is opened or updated. The developer sees results before merging.
`schedule cron: '0 2 * * *'` — runs at 2am every day. A nightly baseline run even when there are no commits.
`workflow_dispatch` — adds a 'Run workflow' button in the GitHub UI. Trigger manually any time.

This combination means: automatic on every commit, automatic on every PR, automatic nightly, and manual on demand.

---

```yaml
jobs:
  performance-test:
    runs-on: ubuntu-latest
```

`jobs` — a workflow can have multiple jobs running in parallel or in sequence.
`performance-test` — the job name. Shown in the GitHub Actions UI.
`runs-on: ubuntu-latest` — use GitHub's hosted Ubuntu runner. Java and Python are pre-installed. JMeter is installed in the steps below.

---

```yaml
    env:
      ADACTIN_HOST:  adactinhotelapp.com
      ADACTIN_PORT:  443
      ADACTIN_PROTO: https
      THREADS:       5
      RAMPUP:        10
      DURATION:      120
      P95_SLA:       3000
      JMETER_VERSION: 5.6.3
```

Same environment variables as Jenkins. All in one place. For different values per branch, use GitHub's environment secrets or variables.

---

```yaml
    steps:

      - name: Checkout repository
        uses: actions/checkout@v4
```

`uses: actions/checkout@v4` — a pre-built action from the GitHub Marketplace. Checks out the repository onto the runner. One line replaces what would be a shell command.

---

```yaml
      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
```

Install Java 17 on the runner. JMeter requires Java. `actions/setup-java` handles download, installation, and PATH configuration automatically.

---

```yaml
      - name: Install JMeter
        run: |
          wget -q https://downloads.apache.org/jmeter/binaries/apache-jmeter-${{ env.JMETER_VERSION }}.tgz
          tar -xzf apache-jmeter-${{ env.JMETER_VERSION }}.tgz
          echo "JMETER_HOME=$PWD/apache-jmeter-${{ env.JMETER_VERSION }}" >> $GITHUB_ENV
```

Download JMeter, extract it, set the JMETER_HOME environment variable for subsequent steps.

`>> $GITHUB_ENV` — the GitHub Actions way of setting an environment variable that persists across steps. Writing to the `$GITHUB_ENV` file makes `JMETER_HOME` available in all subsequent steps.

---

```yaml
      - name: Run JMeter performance test
        run: |
          mkdir -p results
          $JMETER_HOME/bin/jmeter \
            -n \
            -t  jmx/adactin_booking.jmx \
            -Jhost=${{ env.ADACTIN_HOST }} \
            -Jport=${{ env.ADACTIN_PORT }} \
            -Jprotocol=${{ env.ADACTIN_PROTO }} \
            -Jthreads=${{ env.THREADS }} \
            -Jrampup=${{ env.RAMPUP }} \
            -Jduration=${{ env.DURATION }} \
            -l  results/adactin_${{ github.run_number }}.jtl \
            -e  -o results/report \
            -Jjmeter.save.saveservice.print_field_names=true \
            -Jjmeter.save.saveservice.data_type=false \
            -Jjmeter.save.saveservice.sent_bytes=false \
            -Jjmeter.save.saveservice.idle_time=false \
            -Jjmeter.save.saveservice.connect_time=false
```

Identical JMeter command as Jenkins. `${{ github.run_number }}` is GitHub's equivalent of `${BUILD_NUMBER}` — the sequential run number.

`${{ env.THREADS }}` — GitHub Actions syntax for referencing environment variables in `run` blocks.

---

```yaml
      - name: Performance Gate
        run: |
          python3 scripts/check_p95.py \
            results/adactin_${{ github.run_number }}.jtl \
            ${{ env.P95_SLA }}
```

Same `check_p95.py` script. Same logic. Exit 1 fails the workflow. GitHub marks the run as failed. PR cannot be merged if branch protection rules require passing checks.

---

```yaml
      - name: Upload JTL artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: jmeter-results-${{ github.run_number }}
          path: results/
          retention-days: 30
```

`if: always()` — runs even if a previous step failed. You want the JTL even when the gate fails — to debug why it failed.

`uses: actions/upload-artifact@v4` — saves the results folder as a downloadable artifact. Available in the GitHub Actions UI under the run. Retained for 30 days.

---

```yaml
      - name: Publish HTML Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: jmeter-html-report-${{ github.run_number }}
          path: results/report/
          retention-days: 30
```

The JMeter HTML Dashboard is uploaded as a separate artifact. Download it, extract it, open index.html in a browser. Full visual report available for every run."

---

## BLOCK 8 — AZURE DEVOPS INTRO (63:00–67:00)

"Azure DevOps is Microsoft's CI/CD platform. It is the enterprise alternative to GitHub Actions — commonly used in organisations running on Azure, Microsoft 365, or on-premise Microsoft infrastructure.

Three differences from GitHub Actions:

**One — YAML pipelines in `azure-pipelines.yml`.** Same concept as Jenkinsfile and GitHub Actions workflows — Pipeline as Code.

**Two — Microsoft-hosted agents.** Similar to GitHub's hosted runners. Ubuntu, Windows, Mac agents available. Java and Python pre-installed.

**Three — Test results integration.** Azure DevOps has built-in test result publishing. The `PublishTestResults` task reads JTL files and renders pass/fail/duration directly in the Azure DevOps UI — no separate plugin needed.

---

When to choose Azure DevOps:

Your organisation is Microsoft-heavy. Azure cloud. Azure Boards for project management. Azure Repos for Git. Azure Artifacts for packages. When everything is already in the Azure ecosystem, Azure DevOps pipelines are the natural choice.

When to use GitHub Actions instead:

Your code is on GitHub. You want the GitHub PR integration — pipeline status shown directly on the PR. You prefer the open marketplace ecosystem."

---

## BLOCK 9 — AZURE DEVOPS PIPELINE LINE BY LINE (67:00–78:00)

[Open `azure-pipelines.yml` in a text editor.]

"The file is named `azure-pipelines.yml` at the root of the repository. Azure DevOps reads it automatically when you connect the repository.

---

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pr:
  branches:
    include:
      - main
```

`trigger` — run on push to main or develop.
`pr` — run on pull requests targeting main.

Same trigger pattern as GitHub Actions — commit and PR.

---

```yaml
pool:
  vmImage: ubuntu-latest
```

Use Microsoft's hosted Ubuntu agent. Same concept as GitHub's `runs-on: ubuntu-latest`.

---

```yaml
variables:
  adactinHost:    adactinhotelapp.com
  adactinPort:    443
  adactinProto:   https
  jmeterVersion:  5.6.3
  threads:        5
  rampup:         10
  duration:       120
  p95Sla:         3000
  jmeterHome:     $(Agent.BuildDirectory)/apache-jmeter-$(jmeterVersion)
```

`$(Agent.BuildDirectory)` — Azure DevOps built-in variable. The agent's working directory. Used to construct the JMeter installation path.

---

```yaml
steps:

  - task: JavaToolInstaller@0
    displayName: 'Install Java 17'
    inputs:
      versionSpec:     '17'
      jdkArchitectureOption: x64
      jdkSourceOption: PreInstalled
```

`task: JavaToolInstaller@0` — Azure DevOps task for Java setup. `@0` is the task version. Always pin the version — prevents unexpected breaking changes when Microsoft updates the task.

---

```yaml
  - script: |
      wget -q https://downloads.apache.org/jmeter/binaries/apache-jmeter-$(jmeterVersion).tgz
      tar -xzf apache-jmeter-$(jmeterVersion).tgz -C $(Agent.BuildDirectory)
      echo "##vso[task.setvariable variable=JMETER_HOME]$(jmeterHome)"
    displayName: 'Install JMeter $(jmeterVersion)'
```

`##vso[task.setvariable variable=JMETER_HOME]` — Azure DevOps syntax for setting a pipeline variable from a script step. The double-hash `##vso` prefix marks it as a logging command that Azure DevOps intercepts. Equivalent to `>> $GITHUB_ENV` in GitHub Actions.

---

```yaml
  - script: |
      mkdir -p results
      $(JMETER_HOME)/bin/jmeter \
        -n \
        -t  jmx/adactin_booking.jmx \
        -Jhost=$(adactinHost) \
        -Jport=$(adactinPort) \
        -Jprotocol=$(adactinProto) \
        -Jthreads=$(threads) \
        -Jrampup=$(rampup) \
        -Jduration=$(duration) \
        -l  results/adactin_$(Build.BuildNumber).jtl \
        -e  -o results/report \
        -Jjmeter.save.saveservice.print_field_names=true \
        -Jjmeter.save.saveservice.data_type=false \
        -Jjmeter.save.saveservice.sent_bytes=false \
        -Jjmeter.save.saveservice.idle_time=false \
        -Jjmeter.save.saveservice.connect_time=false
    displayName: 'Run JMeter Performance Test'
```

`$(Build.BuildNumber)` — Azure DevOps equivalent of `${BUILD_NUMBER}`. The sequential build number.

`$(adactinHost)` — Azure DevOps variable reference syntax. Same parentheses style throughout.

---

```yaml
  - script: |
      python3 scripts/check_p95.py \
        results/adactin_$(Build.BuildNumber).jtl \
        $(p95Sla)
    displayName: 'Performance Gate — P95 check'
```

Same script. Same logic. Exit 1 fails the Azure DevOps pipeline stage. Build marked failed. PR blocked.

---

```yaml
  - task: PublishTestResults@2
    displayName: 'Publish test results to Azure DevOps'
    condition: always()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles:  results/*.jtl
      failTaskOnFailedTests: false
```

`PublishTestResults` — built-in Azure DevOps task. Reads the JTL and renders results in the Test Results tab of the pipeline run. Green for passing samples, red for failing ones. No external plugin needed.

Note: `testResultsFormat: JUnit` — Azure DevOps can read JTL files as JUnit XML when the format is compatible. For full JTL support you may need a conversion step — but for basic pass/fail counts this works directly.

---

```yaml
  - task: PublishBuildArtifacts@1
    displayName: 'Archive JTL and HTML Report'
    condition: always()
    inputs:
      pathToPublish: results/
      artifactName:  JMeterResults
```

Saves the results folder as a build artifact. Accessible in the Azure DevOps UI under Artifacts. Downloadable. Retained per your pipeline retention policy."

---

## BLOCK 10 — HANDS-ON LAB: GITHUB ACTIONS AND AZURE DEVOPS (78:00–85:00)

[Terminal and browser open.]

"Two hands-on exercises. Five minutes total — one for each platform.

---

**Exercise 1 — GitHub Actions:**

Step 1: Create `.github/workflows/perf-test.yml` in your repository with the workflow we just wrote.

Step 2: Push the file to GitHub. Go to the Actions tab. You will see the workflow running automatically.

Step 3: Watch the steps execute:
```
✅ Checkout repository
✅ Set up Java
✅ Install JMeter
✅ Run JMeter performance test
✅ Performance Gate
✅ Upload JTL artifact
✅ Publish HTML Report
```

Step 4: Click the run. Download the JMeter HTML Report artifact. Open index.html — the full dashboard.

Step 5: Create a pull request. The Actions tab on the PR shows the workflow status — green check or red X. Branch protection rules can require this check to pass before merge is allowed.

---

**Exercise 2 — Azure DevOps:**

Step 1: Push `azure-pipelines.yml` to your repository.

Step 2: In Azure DevOps → Pipelines → New Pipeline → Azure Repos Git → select your repository → Existing Azure Pipelines YAML file → select `azure-pipelines.yml` → Run.

Step 3: Watch the pipeline stages. After completion → click Tests tab — JMeter results shown as pass/fail counts.

Step 4: Click Artifacts → JMeterResults → download the folder → open `report/index.html`.

---

Both pipelines are now running. GitHub Actions for your GitHub repositories. Azure DevOps for your Azure-hosted projects. The JMX, the check_p95.py script, and the data files are identical across both. Only the workflow syntax differs."

---

---

# PART 3 — ADVANCED PIPELINE PATTERNS (85:00–100:00)

---

## BLOCK 11 — PARALLEL EXECUTION (85:00–90:00)

"In all three pipelines so far, the performance test runs as a single sequential job. One JMeter run. One set of results.

Advanced pipelines run multiple tests in parallel:

```
               ┌─ Smoke Test (1 user, 30s) ────────────┐
               │                                        │
Checkout ──────┼─ Load Test (50 users, 5min) ──────────┼──── Gate ── Publish
               │                                        │
               └─ Spike Test (200 users, 30s burst) ───┘
```

All three run simultaneously. The total pipeline time is the longest single test — not the sum of all three. Three tests in 5 minutes instead of 15 minutes.

---

In GitHub Actions:

```yaml
jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Smoke Test
        run: |
          $JMETER_HOME/bin/jmeter -n -t jmx/adactin_booking.jmx \
            -Jthreads=1 -Jduration=30 \
            -l results/smoke.jtl

  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Load Test
        run: |
          $JMETER_HOME/bin/jmeter -n -t jmx/adactin_booking.jmx \
            -Jthreads=50 -Jduration=300 \
            -l results/load.jtl

  spike-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Spike Test
        run: |
          $JMETER_HOME/bin/jmeter -n -t jmx/adactin_booking.jmx \
            -Jthreads=200 -Jduration=30 \
            -l results/spike.jtl

  gate:
    needs: [smoke-test, load-test, spike-test]
    runs-on: ubuntu-latest
    steps:
      - name: Check all gates
        run: |
          python3 scripts/check_p95.py results/smoke.jtl 2000
          python3 scripts/check_p95.py results/load.jtl  3000
          python3 scripts/check_p95.py results/spike.jtl 5000
```

`needs: [smoke-test, load-test, spike-test]` — the gate job waits for all three tests to finish before running. Different SLAs per test type — 2 seconds for smoke, 3 seconds for load, 5 seconds for spike.

Each test type has its own SLA because the load profile is different. Under a spike of 200 users, 5 seconds is acceptable. Under a 1-user smoke test, 2 seconds is the expectation."

---

## BLOCK 12 — ENVIRONMENT-BASED THRESHOLDS (90:00–94:00)

"Different environments have different SLAs. Dev is running on a developer laptop with one CPU. Staging is a scaled-down production replica. Performance thresholds should reflect the environment.

```yaml
# GitHub Actions — environment-based thresholds
jobs:
  performance-test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        environment:
          - name: dev
            host: dev.adactin.internal
            p95_sla: 8000
            threads: 2
          - name: staging
            host: staging.adactin.internal
            p95_sla: 4000
            threads: 10
          - name: prod-like
            host: adactinhotelapp.com
            p95_sla: 3000
            threads: 50

    steps:
      - uses: actions/checkout@v4
      - name: Run test for ${{ matrix.environment.name }}
        run: |
          $JMETER_HOME/bin/jmeter -n -t jmx/adactin_booking.jmx \
            -Jhost=${{ matrix.environment.host }} \
            -Jthreads=${{ matrix.environment.threads }} \
            -l results/adactin_${{ matrix.environment.name }}.jtl

      - name: Gate for ${{ matrix.environment.name }}
        run: |
          python3 scripts/check_p95.py \
            results/adactin_${{ matrix.environment.name }}.jtl \
            ${{ matrix.environment.p95_sla }}
```

`strategy: matrix` — GitHub Actions runs one job instance per matrix entry. Three environments = three parallel jobs. Each job uses its own host and SLA.

The same JMX file. The same test plan. Three different configurations. The matrix expansion handles it automatically.

---

In Jenkins the equivalent uses parameters:

```groovy
pipeline {
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod-like'],
            description: 'Target environment'
        )
    }
    environment {
        P95_SLA = sh(
            script: "python3 scripts/get_sla.py ${params.ENVIRONMENT}",
            returnStdout: true
        ).trim()
    }
}
```

The SLA is looked up from a configuration file based on the selected environment. One Jenkinsfile. Multiple environments. Consistent process."

---

## BLOCK 13 — TREND GATING (94:00–97:00)

"The `relativeFailedThresholdPositive` in the Jenkins Performance Plugin catches single-build regressions. But what about gradual drift — 2% slower per sprint, accumulating over 20 sprints?

A 2% increase per build passes the relative threshold of 20%. But after 20 sprints you are 40% slower than baseline. The Performance Plugin's trend chart shows this visually. But the build never fails.

Trend gating catches it programmatically.

---

```python
# scripts/check_trend.py
import sys, csv, os, glob

def get_p95(jtl_file):
    times = []
    with open(jtl_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('success','').lower().strip() == 'true':
                try: times.append(int(row['elapsed']))
                except: continue
    times.sort()
    return times[int(len(times) * 0.95)] if times else 0

def check_trend(results_dir, current_jtl, drift_threshold_pct):
    # Get all historical JTL files sorted oldest to newest
    all_jtls = sorted(glob.glob(f'{results_dir}/adactin_*.jtl'))
    if len(all_jtls) < 5:
        print('Not enough builds for trend analysis — skipping')
        sys.exit(0)

    # Baseline = average P95 of the last 5 builds
    recent = all_jtls[-5:]
    baseline_p95 = sum(get_p95(f) for f in recent) / len(recent)
    current_p95  = get_p95(current_jtl)
    drift_pct    = ((current_p95 - baseline_p95) / baseline_p95) * 100

    print(f'Baseline P95 (5-build avg): {baseline_p95:.0f}ms')
    print(f'Current P95:                {current_p95}ms')
    print(f'Drift:                      {drift_pct:.1f}%')
    print(f'Drift threshold:            {drift_threshold_pct}%')

    if drift_pct > drift_threshold_pct:
        print(f'TREND GATE FAILED — {drift_pct:.1f}% drift exceeds {drift_threshold_pct}% threshold')
        sys.exit(1)

    print('TREND GATE PASSED')
    sys.exit(0)

if __name__ == '__main__':
    check_trend(sys.argv[1], sys.argv[2], float(sys.argv[3]))
```

Usage in Jenkinsfile:

```groovy
stage('Trend Gate') {
    steps {
        sh '''
            python3 scripts/check_trend.py \
                results/ \
                results/adactin_${BUILD_NUMBER}.jtl \
                15
        '''
    }
}
```

15% drift over the rolling 5-build average triggers a build failure. Gradual degradation is caught before it becomes a client-visible problem."

---

## BLOCK 14 — NOTIFICATION PATTERNS (97:00–100:00)

"Notifications are how the team knows the pipeline needs attention. Three patterns.

---

**Pattern 1 — Email (built-in, all platforms):**

Jenkins:
```groovy
failure {
    mail to:      'team@company.com',
         subject: "PERF FAIL — Build ${BUILD_NUMBER}",
         body:    "P95 exceeded SLA. See: ${BUILD_URL}"
}
```

GitHub Actions:
```yaml
- name: Notify on failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    to: team@company.com
    subject: "PERF FAIL — Run ${{ github.run_number }}"
    body: "P95 exceeded SLA. See: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

---

**Pattern 2 — Slack (most teams prefer this):**

GitHub Actions:
```yaml
- name: Slack notification on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    channel-id: perf-alerts
    slack-message: |
      ❌ *Performance Gate Failed*
      Build: ${{ github.run_number }}
      Branch: ${{ github.ref_name }}
      P95 exceeded SLA of ${{ env.P95_SLA }}ms
      Details: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
  env:
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

The Slack message includes the build number, branch name, the SLA that was breached, and a direct link to the run. One click from the notification to the console log.

---

**Pattern 3 — Teams webhook (Azure DevOps teams):**

```yaml
  - script: |
      curl -H 'Content-Type: application/json' \
           -d '{
             "text": "❌ Performance Gate Failed — Build $(Build.BuildNumber). P95 exceeded $(p95Sla)ms SLA."
           }' \
           $(TEAMS_WEBHOOK_URL)
    displayName: 'Teams notification on failure'
    condition: failed()
```

`$(TEAMS_WEBHOOK_URL)` — stored as a secret variable in Azure DevOps pipeline settings. Never in the YAML file.

---

**The rule for secrets:**

Never put credentials, tokens, or webhook URLs directly in the YAML file. Always use:
- Jenkins: `credentials()` binding
- GitHub Actions: `${{ secrets.SECRET_NAME }}`
- Azure DevOps: `$(SECRET_VARIABLE_NAME)` with the variable marked as secret in pipeline settings

The YAML file is in your repository. It is visible to everyone with repository access. Secrets are stored in the CI/CD platform and injected at runtime. They are never written to logs."

---

---

## MASTER QUICK REFERENCE

```
JENKINS                          GITHUB ACTIONS              AZURE DEVOPS
─────────────────────────────────────────────────────────────────────────
Jenkinsfile                      .github/workflows/*.yml     azure-pipelines.yml
${BUILD_NUMBER}                  ${{ github.run_number }}    $(Build.BuildNumber)
${BUILD_URL}                     ${{ github.server_url }}/…  $(Build.BuildUri)
>> $GITHUB_ENV (not applicable)  >> $GITHUB_ENV              ##vso[task.setvariable]
agent any                        runs-on: ubuntu-latest      pool: vmImage: ubuntu
perfReport()                     upload-artifact             PublishTestResults@2
credentials()                    ${{ secrets.NAME }}         $(SECRET_VAR)

JMETER COMMAND (SAME ON ALL PLATFORMS)
  jmeter -n -t jmx/adactin_booking.jmx \
    -Jhost=adactinhotelapp.com \
    -Jport=443 \
    -Jprotocol=https \
    -Jthreads=5 \
    -Jrampup=10 \
    -Jduration=120 \
    -l results/adactin_BUILD.jtl \
    -e -o results/report \
    -Jjmeter.save.saveservice.print_field_names=true

PERFORMANCE GATE (check_p95.py — same on all platforms)
  exit 0 → P95 within SLA → pipeline passes → promotion allowed
  exit 1 → P95 exceeds SLA → pipeline fails → promotion blocked

JENKINS PERFORMANCE PLUGIN THRESHOLDS
  errorFailedThreshold:            0.5   fail if error% > 0.5%
  errorUnstableThreshold:          0.1   unstable if error% > 0.1%
  relativeFailedThresholdPositive:  20   fail if P95 increases > 20%

ADVANCED PATTERNS
  Parallel jobs     → smoke + load + spike run simultaneously
  Matrix strategy   → same test, 3 environments, 3 SLAs, one workflow
  Trend gating      → check_trend.py: fail if drift > 15% vs 5-build avg
  Slack alert       → slackapi/slack-github-action@v1 on failure
  Teams alert       → curl POST to webhook URL on failure
  Secrets           → never in YAML — always in platform secrets store

WHEN TO USE EACH PLATFORM
  Jenkins         → on-premise infra, complex agents, enterprise control
  GitHub Actions  → code on GitHub, small-medium teams, zero maintenance
  Azure DevOps    → Microsoft ecosystem, Azure cloud, enterprise governance
```

---

*CI/CD for JMeter — Master Script: Parts 1, 2, 3*
*Visvashwarr Venugopal | Sr. Technical Lead — Performance Engineering*
*100 Minutes | Adactin Hotel | Jenkins + GitHub Actions + Azure DevOps*
