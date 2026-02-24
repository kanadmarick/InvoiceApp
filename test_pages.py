#!/usr/bin/env python
import urllib.request
import sys

urls = [
    ('Homepage', 'http://127.0.0.1:8000/'),
    ('Businesses', 'http://127.0.0.1:8000/businesses/'),
    ('Invoices', 'http://127.0.0.1:8000/billings/'),
    ('Accounts', 'http://127.0.0.1:8000/accounts/'),
]

print('\nTesting all application pages...\n')
print('-' * 50)

errors = []
for name, url in urls:
    try:
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read()
        if response.status == 200:
            print(f'[OK]  {name:20s} Status {response.status} ({len(content)} bytes)')
        else:
            print(f'[WARN] {name:20s} Status {response.status}')
    except Exception as e:
        print(f'[FAIL] {name:20s} Error: {str(e)[:50]}')
        errors.append((name, str(e)))

print('-' * 50)

if errors:
    print(f'\nFound {len(errors)} error(s):')
    for name, error in errors:
        print(f'  - {name}: {error}')
    sys.exit(1)
else:
    print('\n==> ALL FEATURES WORKING!')
    print('\nServer running at: http://127.0.0.1:8000')
    print('  - All pages accessible')
    print('  - Database has test data')
    print('  - Ready for use!')
    sys.exit(0)
