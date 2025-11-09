# XRetriever




**XRetriever** is a powerful Python package for X-ray Diffraction (XRD) pattern matching and crystal structure retrieval. It provides state-of-the-art algorithms for matching experimental XRD patterns to crystal structure databases, enabling rapid phase identification and materials characterization.



### Core Capabilities
- **Robust Peak Detection**: Advanced algorithms with Savitzky-Golay filtering and baseline removal
- **Intelligent Pattern Matching**: Hungarian algorithm-based optimal peak assignment
- **Dual Scoring Metrics**:
  - **Weighted Score**: 70% position + 30% intensity similarity
  - **FOM (Figure of Merit)**: ICDD-standard quantitative matching metric
- **Element-Based Filtering**: Fast candidate screening by chemical composition
- **Flexible Input**: Support for CSV, TXT, and direct peak data input

### Advanced Features
- **Combined Scoring Mode**: Get both weighted and FOM scores simultaneously
- **Top-N Peak Selection**: Automatically extract and normalize the strongest peaks
- **Configurable Tolerances**: Adjust position tolerance (default: ±0.2° in 2θ)
- **Comprehensive Results**: Detailed matching information with peak-by-peak analysis

## Installation

### From PyPI (Recommended)
```bash
pip install XRetriever
```


