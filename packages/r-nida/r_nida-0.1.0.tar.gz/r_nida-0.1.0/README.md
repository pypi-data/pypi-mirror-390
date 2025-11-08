# Reverse NIDA

A Python package that attempts to reverse engineer how NIDA (National Identification Authority) numbers are generated and extract basic information from National Identification Numbers (NIN) without using the official NIDA API.

## ⚠️ Disclaimer

This project is for educational and research purposes only. It attempts to understand the structure and patterns in NIDA numbers through reverse engineering. The accuracy of extracted information is not guaranteed, and this should not be used for official verification purposes.


## 🚀 Installation

### From PyPI
```bash
pip install reverse-nida
```

## 📖 Usage

### Simple Usage (Recommended)
```python
from r_nida import get_basic_info

# Analyze a NIDA number (supports both dashed and compact formats)
nin_dashed = "xxxxxxxx-xxxxx-xxxxx-xx"
nin_compact = "xxxxxxxxxxxxxxxxxxxx"

# Get basic information
info = get_basic_info(nin_dashed, debug=False)
print(info)
# Output: {
#   'BIRTHDATE': '',
#   'GENDER': '',
#   'REGIONCODE':'',
#   'REGION': '',
#   'DISTRICT': '',
#   'WARDCODE':'',
#   'WARD': '',
#   'WARDCODE': '',
#   'STREET': '',
#   'PLACES':'',
# }

# Get full information with debug
info = service.get_basic_info("xxxxxxxx-xxxxx-xxxxx-xx", debug=True)
```

### Setup Development Environment
```bash
git clone https://github.com/Henryle-hd/reverse-nida.git
cd reverse-nida
```