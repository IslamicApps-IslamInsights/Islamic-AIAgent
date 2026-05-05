# 🚀 Graphify Quick Start Guide

Get started with project indexing and knowledge graphs in 5 minutes!

## Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## 5-Minute Quickstart

### Step 1: Index Your Project

```bash
cd scripts
python graphify_cli.py index --project-path .. --name noor
```

Expected output: Indexing complete with statistics

### Step 2: Build Knowledge Graph

```bash
python graphify_cli.py build-graph --index-name noor --graph-name noor_kg
```

Expected output: Graph built successfully

### Step 3: View Project Health

```bash
python graphify_cli.py health --graph-name noor_kg
```

Expected output: Health report with complexity hotspots

### Step 4: Export for Visualization

```bash
python graphify_cli.py export --graph-name noor_kg --format json --output noor.json
```

## Using the REST API

### Start the Backend Server

```bash
python backend/api/web_api.py --port 5010
```

### Index via API

```bash
curl -X POST http://localhost:5010/api/indexing/index \
  -H "Content-Type: application/json" \
  -d '{"name": "noor"}'
```

### Get Health Report

```bash
curl http://localhost:5010/api/indexing/assistant/health?graph_name=noor_kg
```

## Common Workflows

### Workflow 1: Code Review
1. Index project
2. Get health report
3. Export to JSON for team review

### Workflow 2: New Developer Onboarding
1. Index project
2. Generate architecture overview
3. Get module documentation

### Workflow 3: Refactoring
1. Identify complexity hotspots
2. Analyze impact of changes
3. Refactor with confidence

## Tips & Tricks

✅ **Faster Indexing**: Exclude large directories
✅ **Rebuild After Changes**: Re-index after major refactoring
✅ **Visualize with Gephi**: Export to GEXF format
✅ **Monitor Growth**: Track metrics over time

## Troubleshooting

**Q: Indexing hangs?**
A: Check excluded directories, increase timeout

**Q: Graph not found?**
A: Run list-graphs to see available graphs

**Q: Memory usage high?**
A: Cleanup old graphs

---

See [GRAPHIFY_INDEXING_GUIDE.md](GRAPHIFY_INDEXING_GUIDE.md) for complete documentation.

**Happy analyzing! 🚀**
