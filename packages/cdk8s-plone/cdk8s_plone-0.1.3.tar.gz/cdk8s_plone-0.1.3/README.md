# CDK8S Plone

A CDK8S library for deploying Plone CMS to Kubernetes.

This library provides constructs to bootstrap a Plone deployment on a Kubernetes cluster using the [CDK8S](https://cdk8s.io) framework.

## Features

* **Backend**: Plone backend (API with `plone.volto` or Classic-UI)
* **Frontend**: Plone Volto (modern React-based user interface)
* **Varnish Caching**: Optional HTTP caching layer using [kube-httpcache](https://github.com/mittwald/kube-httpcache) with cluster-wide cache invalidation
* **High Availability**: Configurable replicas with PodDisruptionBudgets
* **Multi-language Support**: Published to npm (TypeScript/JavaScript) and PyPI (Python)

## Installation

### TypeScript/JavaScript

Create a new CDK8S project (or use an existing one):

```bash
cdk8s init typescript-app
```

Install the library:

```bash
npm install @bluedynamics/cdk8s-plone
```

Package: [@bluedynamics/cdk8s-plone](https://www.npmjs.com/package/@bluedynamics/cdk8s-plone)

### Python

Create a new CDK8S project:

```bash
cdk8s init python-app
```

Install the library:

```bash
pip install cdk8s-plone
```

Package: [cdk8s-plone](https://pypi.org/project/cdk8s-plone/)

## Quick Start

### Basic Plone Deployment

```python
import { App, Chart } from 'cdk8s';
import { Plone, PloneVariant } from '@bluedynamics/cdk8s-plone';

const app = new App();
const chart = new Chart(app, 'PloneDeployment');

new Plone(chart, 'my-plone', {
  variant: PloneVariant.VOLTO,
  backend: {
    image: 'plone/plone-backend:6.0.10',
    replicas: 3,
  },
  frontend: {
    image: 'plone/plone-frontend:16.0.0',
    replicas: 2,
  },
});

app.synth();
```

### With Varnish HTTP Cache

```python
import { PloneHttpcache } from '@bluedynamics/cdk8s-plone';

const plone = new Plone(chart, 'my-plone', {
  variant: PloneVariant.VOLTO,
  backend: { image: 'plone/plone-backend:6.0.10' },
  frontend: { image: 'plone/plone-frontend:16.0.0' },
});

new PloneHttpcache(chart, 'cache', {
  plone: plone,
  existingSecret: 'varnish-secret',
  replicas: 2,
});
```

### Generate Kubernetes Manifests

```bash
cdk8s synth
```

The manifests are stored in the `dist/` directory.

For a complete example, see the [example project](https://github.com/bluedynamics/cdk8s-plone-example).

## Prerequisites

* **kubectl** - Command-line tool for deploying Kubernetes manifests. [Install kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
* **Helm** (optional) - Only needed if generating Helm charts. [Install Helm](https://helm.sh/docs/intro/install/)
* **Node.js** - For TypeScript/JavaScript development
* **Python 3.8+** - For Python development

## API Documentation

For complete API documentation, see [API.md](./API.md).

### Key Constructs

#### `Plone`

Main construct for deploying Plone CMS. Supports two variants:

* **VOLTO**: Modern React frontend with REST API backend (default)
* **CLASSICUI**: Traditional server-side rendered Plone

Properties:

* `backendServiceName` - Name of the backend Kubernetes service
* `frontendServiceName` - Name of the frontend service (VOLTO only)
* `variant` - Deployment variant (VOLTO or CLASSICUI)
* `siteId` - Plone site ID in ZODB (default: 'Plone')

#### `PloneHttpcache`

Varnish HTTP caching layer using the [kube-httpcache](https://github.com/mittwald/kube-httpcache) Helm chart.

Properties:

* `httpcacheServiceName` - Name of the Varnish service

### Configuration Options

#### `PloneOptions`

* `version` - Version of your project
* `siteId` - Plone site ID (default: 'Plone')
* `variant` - PloneVariant.VOLTO or PloneVariant.CLASSICUI (default: VOLTO)
* `backend` - Backend configuration (PloneBaseOptions)
* `frontend` - Frontend configuration (PloneBaseOptions, required for VOLTO)
* `imagePullSecrets` - Image pull secrets for private registries

#### `PloneBaseOptions`

Configuration for backend or frontend:

**Container:**

* `image` - Container image (e.g., 'plone/plone-backend:6.0.10')
* `imagePullPolicy` - Pull policy (default: 'IfNotPresent')
* `replicas` - Number of replicas (default: 2)
* `environment` - Environment variables (cdk8s-plus-30.Env)

**Resources:**

* `requestCpu` / `limitCpu` - CPU requests/limits
* `requestMemory` / `limitMemory` - Memory requests/limits

**High Availability:**

* `minAvailable` - Min pods during updates (for PodDisruptionBudget)
* `maxUnavailable` - Max unavailable pods during updates

**Health Probes:**

* `readinessEnabled` - Enable readiness probe (default: true)
* `readinessInitialDelaySeconds` / `readinessTimeoutSeconds` / `readinessPeriodSeconds`
* `readinessSuccessThreshold` / `readinessFailureThreshold`
* `livenessEnabled` - Enable liveness probe (default: false, recommended true for frontend)
* `livenessInitialDelaySeconds` / `livenessTimeoutSeconds` / `livenessPeriodSeconds`
* `livenessSuccessThreshold` / `livenessFailureThreshold`

**Annotations:**

* `annotations` - Deployment metadata annotations
* `podAnnotations` - Pod template annotations (e.g., for Prometheus)
* `serviceAnnotations` - Service annotations (e.g., for external-dns)

#### `PloneHttpcacheOptions`

* `plone` - Plone construct to attach cache to (required)
* `varnishVcl` - VCL configuration as string
* `varnishVclFile` - Path to VCL configuration file
* `existingSecret` - Kubernetes secret for Varnish admin credentials
* `replicas` - Number of Varnish replicas (default: 2)
* `requestCpu` / `limitCpu` - CPU resources
* `requestMemory` / `limitMemory` - Memory resources
* `servicemonitor` - Enable Prometheus ServiceMonitor (default: false)
* `exporterEnabled` - Enable Prometheus exporter sidecar (default: true)
* `chartVersion` - kube-httpcache Helm chart version (default: latest)

## Development

This project uses [Projen](https://projen.io/) to manage project configuration. **Do not edit generated files directly.**

### Setup

Clone the repository and install dependencies:

```bash
nvm use lts/*
corepack enable
npx projen
```

### Common Commands

```bash
# Run tests
npx projen test

# Run tests in watch mode
npx projen test:watch

# Build (compile TypeScript + generate JSII bindings)
npx projen build

# Lint
npx projen eslint

# Generate API documentation
npx projen docgen

# Package for distribution
npx projen package-all
```

### Making Changes

1. Edit `.projenrc.ts` for project configuration changes
2. Run `npx projen` to regenerate project files
3. Make code changes in `src/`
4. Run tests and update snapshots if needed: `npx projen test -- -u`

## References

* [CDK8S Documentation](https://cdk8s.io/)
* [Kubernetes Probes Documentation](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
* [kube-httpcache Helm Chart](https://github.com/mittwald/kube-httpcache)
* [Example Project](https://github.com/bluedynamics/cdk8s-plone-example)

## License

See [LICENSE](./LICENSE) file.
