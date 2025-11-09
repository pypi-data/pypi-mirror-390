<div align="center">

# 🌟 ASTRA: Autonomous System for Transient Research & Analysis

**Discover astronomical transients without API access**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)]()

</div>

ASTRA is a fully autonomous astronomical transient discovery engine that identifies scientifically interesting supernovae, cataclysmic variables, and rare stellar phenomena using **only publicly available data sources**—no API keys required.

---

## 🌟 Latest Discovery

**AT2025abao** - Luminous Red Nova at magnitude 15.1
- **Anomaly Score**: 8.0/10 (HIGH PRIORITY)
- **Discovery Date**: 2025-11-06
- **Status**: 🔴 Immediate spectroscopy needed
- [View Full Report](./discoveries/2025-11-06_AT2025abao/index.md)

---

## 🔭 Why ASTRA?

### **The Problem**
Most transient discovery systems require:
- ❌ Expensive API subscriptions
- ❌ Proprietary database access  
- ❌ Institutional credentials
- ❌ Complex infrastructure

### **The Solution**
ASTRA uses **publicly available data** from:
- ✅ Rochester Astronomy Supernova Page
- ✅ Astronomer's Telegram (ATel) public pages
- ✅ TNS public listings
- ✅ Gaia DR3 (for cross-matching)

**Cost**: $0 • **Setup Time**: 5 minutes • **Discovery Rate**: 11.4%

---

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/Shannon-Labs/astra.git
cd astra

# Create virtual environment
python3 -m venv astra_env
source astra_env/bin/activate  # On Windows: astra_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python tests/test_infrastructure.py
# Should see: 🎉 ASTRA IS READY FOR DISCOVERY OPS
```

### Your First Discovery (30 seconds)

```bash
# Run the discovery pipeline (cross-platform)
astra --advanced

# Or use the traditional shell script
./scripts/run_advanced.sh

# View results
cat advanced_report

# Check detailed summary
cat latest_discovery/summary.txt
```

**Expected Output:**
```
🚀 ASTRA Advanced Discovery System
=====================================
✅ Found 35 bright transients
✅ Found 4 high-priority anomalies

🎯 TOP DISCOVERY: AT2025abao (Score: 8.0)
   Type: LRN (Luminous Red Nova)
   Magnitude: 15.1
   Action: Immediate spectroscopy
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Discovery Rate** | 11.4% (4 anomalies per 35 transients) |
| **Runtime** | ~5-10 seconds per pipeline |
| **Data Freshness** | Live from public sources |
| **Resource Usage** | <100 MB RAM, ~50 KB disk per run |
| **Cost** | $0 (no API fees) |
| **Latency** | 1-2 days vs. TNS (acceptable for bright objects) |

---

## 🎯 What Can You Discover?

ASTRA identifies:

- **🌟 Luminous Red Novae** (LRNe) - Rare stellar mergers
- **💥 Supernovae** - Peculiar Type Ia, IIn, Ibn
- **⚡ Cataclysmic Variables** - Unusual outbursts
- **❓ Unknown Phenomena** - Things that don't fit categories

**All bright enough for 2-4m telescope follow-up!**

---

## 🔬 How It Works

### 1. **Data Collection** (`src/transient_scraper.py`)
Scrapes public transient pages and extracts:
- Object IDs (AT2025*, SN2025*)
- Magnitudes
- Types (when available)
- Coordinates (when available)

### 2. **Anomaly Detection** (`src/enhanced_discovery_v2.py`)
Multi-factor scoring algorithm:
- **Brightness**: m < 16.0 = +3 points
- **Unknown Type**: +2 points  
- **Rare Type** (LRN, Ibn): +5 points
- **Gaia Match**: +1 point + proper motion
- **High Proper Motion**: +3 points

**Score ≥ 5.0** = High priority for follow-up

### 3. **Discovery Packaging** (`scripts/package_discovery.py`)
Creates publication-ready packages:
- ATel/TNS-style reports
- Observation plans
- Photometric data tables
- System logs for reproducibility

---

## 📁 Repository Structure

```
astra/
├── LICENSE                           # MIT License
├── CITATION.cff                      # Citation metadata
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package installer
│
├── src/                              # Core source code
│   ├── __init__.py                   # Package API
│   ├── transient_scraper.py          # Data collection
│   ├── astra_discovery_engine.py     # Basic detection
│   └── enhanced_discovery_v2.py      # Advanced scoring
│
├── scripts/                          # User-facing scripts
│   ├── run_advanced.sh              # Shell script (Linux/macOS)
│   ├── run_discovery.py             # Python entry point (cross-platform)
│   └── package_top_discoveries.py   # Package discoveries
│
├── tests/                            # Test suite
│   └── test_infrastructure.py       # Validation tests
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md              # System design and components
│   ├── SCIENTIFIC_METHOD.md         # Discovery methodology
│   ├── QUICKSTART.md                # Detailed setup guide
│   └── PUBLICATION_GUIDE.md         # How to publish discoveries
│
├── discoveries/                      # Packaged discoveries
│   └── TEMPLATE/                    # Template for new
│
├── .github/                          # GitHub workflows
│   └── workflows/
│       ├── CI.yml                   # Continuous integration
│       ├── discovery.yml            # Automated discovery runs
│       └── release.yml              # Release management

├── .gitignore                        # Git ignore rules
├── CHANGELOG.md                      # Version history
└── CITATION.cff                      # Academic citation metadata
```

---

## 📚 Documentation

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Scientific Methodology](./docs/SCIENTIFIC_METHOD.md)** - How scoring works
- **[Architecture Overview](./docs/ARCHITECTURE.md)** - System design and components
- **[Publication Guide](./docs/PUBLICATION_GUIDE.md)** - How to publish discoveries

---

## 🤝 Contributing

We welcome contributions from the astronomy community!

- **Report issues**: [GitHub Issues](https://github.com/Shannon-Labs/astra/issues)
- **Add features**: See [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Improve docs**: Fix typos, add examples
- **Share discoveries**: Submit follow-up observations

### Development Setup

```bash
git clone https://github.com/Shannon-Labs/astra.git
cd astra
python3 -m venv astra_env
source astra_env/bin/activate
pip install -e .[dev]
```

---

## 📜 Citation

If you use ASTRA in your research, please cite:

```bibtex
@software{astra2025,
  author = {{ASTRA Collaboration}},
  title = {ASTRA: Autonomous System for Transient Research & Analysis},
  year = {2025},
  publisher = {Shannon Labs},
  url = {https://github.com/Shannon-Labs/astra},
  version = {1.0.0}
}
```

---

## 🌌 Mission Statement

ASTRA democratizes transient discovery by providing autonomous, API-free tools that enable astronomers worldwide to identify scientifically interesting phenomena using only public data sources.

**Every silence is an opportunity. Every anomaly is a frontier.**

---

## 📊 Current Status

- **Version**: 2.0.0
- **Status**: 🟢 Production Ready
- **Last Run**: {{ current date }}
- **Discoveries**: {{ your latest discoveries }}
- **Tests**: All passing
- **CI/CD**: Automated testing and deployment

---

<div align="center">

**🌟 The universe awaits your discoveries. 🌟**

*Share ASTRA • Discover Transients • Publish Science*

</div>