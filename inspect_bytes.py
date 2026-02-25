"""Corrige los patrones restantes de emojis corruptos en admin.py."""

raw = open('gestion/admin.py', 'rb').read()

# Patrones restantes identificados con sus correcciones
# b'\xc3\xa2\xe2\x82\xac\xe2\x80' -> parte de un emoji de warning ⚠️
# b'\xc3\xa2\xc5\xa1\xc2\xa0\xc3' -> parte de emoji
# b'\xc3\xa2\xc2\x9d\xc5\x92 '   -> ❌ X roja

# Veamos qué lineas tienen cada patron
import re
patterns = [
    b'\xc3\xa2\xe2\x82\xac\xe2\x80',
    b'\xc3\xa2\xc5\xa1\xc2\xa0',
    b'\xc3\xa2\xc2\x9d\xc5\x92',
]

lines = raw.split(b'\r\n')
for pat in patterns:
    for i, line in enumerate(lines, 1):
        if pat in line:
            print(f"L{i} ({pat!r}): {line[:100]!r}")
