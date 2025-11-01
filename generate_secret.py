import secrets

print("\n" + "="*60)
print("🔐 SECRET KEY GENERATOR")
print("="*60)
print("\nYour SECRET_KEY for Vercel:")
print("-" * 60)
secret_key = secrets.token_hex(32)
print(secret_key)
print("-" * 60)
print("\nCopy this key and use it in Vercel environment variables!")
print("="*60 + "\n")
