# thepricer-utils

Tiny helpers for price explainers (formatting, ranges, hours-to-afford).  
**Homepage:** https://www.thepricer.org/

## Install
```bash
pip install thepricer-utils
```

## Usage
```python
from thepricer_utils import format_price, midpoint, hours_to_afford

print(format_price(12.99, currency="$", per="lb"))      # "$12.99 per lb"
print(midpoint(9.0, 11.0))                              # 10.0
print(hours_to_afford(28.50, 15.0))                     # 1.9
```
