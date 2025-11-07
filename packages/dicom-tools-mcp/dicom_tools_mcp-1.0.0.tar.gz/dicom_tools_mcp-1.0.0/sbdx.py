import pyotp

key = 'QSKZ3GQR7WZXFP676HOEWX7UBMOQSHHZ'
totp = pyotp.TOTP(key)
print(totp.now())