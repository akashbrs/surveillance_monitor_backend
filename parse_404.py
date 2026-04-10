import sys

with open('error_page.txt', encoding='cp1252', errors='replace') as f:
    html = f.read()

import re
match = re.search(r'(Using the URLconf defined in.*?)(?=</p>)', html, re.DOTALL)
if match:
    print(match.group(1))

lis = re.findall(r'<li>(.*?)</li>', html, re.DOTALL)
for li in lis:
    print(re.sub(r'<[^>]+>', '', li).strip())
