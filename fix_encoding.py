"""Corrige los patrones restantes de emojis corruptos en admin.py."""

raw = open('gestion/admin.py', 'rb').read()

# Patrones exactos con sus reemplazos correctos
replacements = [
    # ⚠️ warning + variante selector (xC3xA2 xC5xA1 xC2xA0 xC3xAF xC2xB8 xC2x8F)
    (b'\xc3\xa2\xc5\xa1\xc2\xa0\xc3\xaf\xc2\xb8\xc2\x8f', '⚠️'.encode('utf-8')),
    # — em dash (xC3xA2 xE2x82xAC xE2x80x9D)
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', ' —'.encode('utf-8')),
    # ❌ X roja (xC3xA2 xC2x9D xC5x92)
    (b'\xc3\xa2\xc2\x9d\xc5\x92', '❌'.encode('utf-8')),
]

fixed = raw
total = 0
for bad, good in replacements:
    count = fixed.count(bad)
    if count:
        fixed = fixed.replace(bad, good)
        print(f'  {count}x {bad!r} -> {good!r}')
        total += count

# Verificar UTF-8
try:
    text = fixed.decode('utf-8-sig')
    open('gestion/admin.py', 'wb').write(fixed)
    print(f'\nTotal {total} reemplazos. UTF-8 valido. Guardado.')
    # Mostrar las lineas corregidas
    for ln in [78, 277, 278, 664, 761, 762, 800]:
        lines = text.split('\n')
        if ln <= len(lines):
            print(f'L{ln}: {lines[ln-1].strip()[:80]}')
except Exception as e:
    print(f'ERROR: {e}')
