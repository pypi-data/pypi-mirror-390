# InfraMind CLI

Command-line tool for easy integration with InfraMind CI/CD optimization engine.

## Installation

```bash
# Install from PyPI (once published)
pip install InfraMind

# Or install from source
cd cli
pip install -e .
```

## Quick Start

```bash
# Set your InfraMind API URL (optional, defaults to localhost)
export INFRAMIND_URL=http://inframind.example.com:8081
export INFRAMIND_API_KEY=your-api-key

# Get optimization suggestions
inframind optimize --repo myorg/myrepo --branch main

# Report build results
inframind report --repo myorg/myrepo --branch main \
  --duration 180 --status success --cpu 8 --memory 16384
```

## Commands

### `optimize`

Get optimization suggestions for your build.

```bash
inframind optimize --repo REPO --branch BRANCH [OPTIONS]

Options:
  --repo TEXT              Repository name (required)
  --branch TEXT            Branch name (default: main)
  --build-type TEXT        Build type (default: release)
  --previous-duration INT  Previous build duration in seconds
  --format [human|json|env|shell]  Output format (default: human)
```

**Output formats:**

- `human` - Human-readable output
- `json` - JSON output for programmatic use
- `env` - Export statements for shell evaluation
- `shell` - Variable assignments for sourcing

**Examples:**

```bash
# Human-readable output
inframind optimize --repo myorg/myrepo --branch main

# JSON output
inframind optimize --repo myorg/myrepo --branch main --format json

# Use in shell scripts
eval $(inframind optimize --repo myorg/myrepo --branch main --format env)
echo "Using $INFRAMIND_CPU CPUs"

# Source variables
source <(inframind optimize --repo myorg/myrepo --branch main --format shell)
```

### `report`

Report build results back to InfraMind for ML training.

```bash
inframind report --repo REPO --branch BRANCH --duration SECONDS --status STATUS [OPTIONS]

Options:
  --repo TEXT          Repository name (required)
  --branch TEXT        Branch name (default: main)
  --duration INT       Build duration in seconds (required)
  --status [success|failure]  Build status (required)
  --cpu INT            CPU cores used
  --memory INT         Memory used in MB
  --format [human|json]  Output format (default: human)
```

**Example:**

```bash
inframind report --repo myorg/myrepo --branch main \
  --duration 245 --status success --cpu 8 --memory 16384
```

### `health`

Check InfraMind API health status.

```bash
inframind health [OPTIONS]

Options:
  --format [human|json]  Output format (default: human)
```

### `config`

Manage CLI configuration (stores settings in `~/.inframind/config`).

```bash
inframind config [OPTIONS]

Options:
  --url TEXT      Set API URL
  --api-key TEXT  Set API key
```

**Example:**

```bash
# Set configuration
inframind config --url http://inframind.example.com:8081 --api-key YOUR_KEY

# View current configuration
inframind config
```

## Environment Variables

- `INFRAMIND_URL` - API base URL (default: `http://localhost:8081`)
- `INFRAMIND_API_KEY` - API authentication key

## Integration Examples

### Jenkins Pipeline

```groovy
pipeline {
  stages {
    stage('Optimize') {
      steps {
        script {
          sh 'pip install InfraMind'
          env.OPTS = sh(
            script: "inframind optimize --repo ${env.GIT_URL} --branch ${env.BRANCH_NAME} --format shell",
            returnStdout: true
          ).trim()
          sh "source <(echo '${env.OPTS}')"
        }
      }
    }
    stage('Build') {
      steps {
        sh 'make build -j${INFRAMIND_CPU}'
      }
    }
    post {
      always {
        sh """
          inframind report --repo ${env.GIT_URL} --branch ${env.BRANCH_NAME} \
            --duration \$BUILD_DURATION --status \$BUILD_STATUS
        """
      }
    }
  }
}
```

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install InfraMind CLI
        run: pip install InfraMind

      - name: Get Optimization Suggestions
        id: optimize
        env:
          INFRAMIND_URL: ${{ secrets.INFRAMIND_URL }}
          INFRAMIND_API_KEY: ${{ secrets.INFRAMIND_API_KEY }}
        run: |
          inframind optimize --repo ${{ github.repository }} --branch ${{ github.ref_name }} --format env >> $GITHUB_ENV

      - name: Build
        run: make build -j${INFRAMIND_CPU}

      - name: Report Results
        if: always()
        env:
          INFRAMIND_URL: ${{ secrets.INFRAMIND_URL }}
          INFRAMIND_API_KEY: ${{ secrets.INFRAMIND_API_KEY }}
        run: |
          inframind report --repo ${{ github.repository }} --branch ${{ github.ref_name }} \
            --duration ${{ job.duration }} --status ${{ job.status }}
```

### GitLab CI

```yaml
build:
  stage: build
  before_script:
    - pip install InfraMind
    - inframind optimize --repo ${CI_PROJECT_PATH} --branch ${CI_COMMIT_BRANCH} --format env > opts.env
    - source opts.env
  script:
    - make build -j${INFRAMIND_CPU}
  after_script:
    - |
      inframind report --repo ${CI_PROJECT_PATH} --branch ${CI_COMMIT_BRANCH} \
        --duration ${CI_JOB_DURATION} --status ${CI_JOB_STATUS}
```

### Shell Script

```bash
#!/bin/bash

# Get optimization suggestions
eval $(inframind optimize --repo myorg/myrepo --branch main --format env)

# Use the suggestions
echo "Building with $INFRAMIND_CPU CPUs and ${INFRAMIND_MEMORY}MB memory"

START_TIME=$(date +%s)

# Run your build
make build -j${INFRAMIND_CPU}
BUILD_STATUS=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Report results
if [ $BUILD_STATUS -eq 0 ]; then
  STATUS="success"
else
  STATUS="failure"
fi

inframind report --repo myorg/myrepo --branch main \
  --duration $DURATION --status $STATUS \
  --cpu $INFRAMIND_CPU --memory $INFRAMIND_MEMORY
```

## Development

```bash
# Install in development mode
cd cli
pip install -e .

# Run directly
python inframind.py optimize --repo test/repo --branch main
```

## License

MIT License - see [LICENSE](../LICENSE) for details.
