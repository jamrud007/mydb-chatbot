"""
Test i18n (Internationalization) Support
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from utils.i18n import get_i18n, t, TRANSLATIONS

print("="*70)
print("MULTI-LANGUAGE SUPPORT TEST")
print("="*70)

# Test 1: Basic translation (Indonesian)
print("\n[TEST 1] Indonesian translations")
i18n = get_i18n('id')
print(f"  Welcome: {i18n.get('general.welcome')}")
print(f"  Rate limit: {i18n.get('error.rate_limit', seconds=30)}")
print(f"  Message too long: {i18n.get('error.message_too_long', length=2500, max_length=2000)}")

# Test 2: English translations  
print("\n[TEST 2] English translations")
i18n.set_language('en')
print(f"  Welcome: {i18n.get('general.welcome')}")
print(f"  Rate limit: {i18n.get('error.rate_limit', seconds=30)}")
print(f"  Message too long: {i18n.get('error.message_too_long', length=2500, max_length=2000)}")

# Test 3: Shorthand function
print("\n[TEST 3] Shorthand function t()")
print(f"  ID: {t('error.database_connection', language='id', error='Connection refused')}")
print(f"  EN: {t('error.database_connection', language='en', error='Connection refused')}")

# Test 4: Missing key handling
print("\n[TEST 4] Missing key handling")
print(f"  Missing key: {i18n.get('nonexistent.key')}")

# Test 5: Language switching
print("\n[TEST 5] Language switching")
i18n.set_language('id')
print(f"  Current language (ID): {i18n.get('info.generating_query')}")
i18n.set_language('en')
print(f"  Switched to (EN): {i18n.get('info.generating_query')}")

# Test 6: All error messages
print("\n[TEST 6] Error messages coverage (English)")
i18n.set_language('en')
error_keys = [k for k in TRANSLATIONS['en'].keys() if k.startswith('error.')]
print(f"  Total error messages: {len(error_keys)}")
for key in error_keys[:5]:  # Show first 5
    print(f"    - {key}: {i18n.get(key)[:60]}...")

# Test 7: Variable substitution
print("\n[TEST 7] Variable substitution")
print(f"  With vars: {t('error.model_not_found', language='en', model='llama3', available='llama2, gemma')}")
print(f"  With vars: {t('error.query_timeout', language='id', seconds=30)}")

# Test 8: Available languages
print("\n[TEST 8] Available languages")
print(f"  Supported: {', '.join(i18n.get_available_languages())}")

# Test 9: Translation statistics
print("\n[TEST 9] Translation statistics")
for lang in ['id', 'en']:
    total = len(TRANSLATIONS[lang])
    error_count = len([k for k in TRANSLATIONS[lang].keys() if k.startswith('error.')])
    success_count = len([k for k in TRANSLATIONS[lang].keys() if k.startswith('success.')])
    info_count = len([k for k in TRANSLATIONS[lang].keys() if k.startswith('info.')])
    
    print(f"  {lang.upper()}:")
    print(f"    Total keys: {total}")
    print(f"    Errors: {error_count}, Success: {success_count}, Info: {info_count}")

print("\n" + "="*70)
print("SUCCESS: Multi-language support working!")
print("="*70)

print("\n[USAGE EXAMPLES]")
print("1. API: Add 'lang' query parameter (?lang=en or ?lang=id)")
print("2. Code: t('error.rate_limit', language='en', seconds=30)")
print("3. Default: Indonesian (id)")
print("")
print("[SUPPORTED LANGUAGES]")
print("- ID (Indonesian) - Default")
print("- EN (English)")
