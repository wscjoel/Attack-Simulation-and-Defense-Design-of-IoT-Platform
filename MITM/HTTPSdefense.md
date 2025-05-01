### 🔒Switch to HTTPS (Defense)

Uncomment the `ssl_context` line in `server.py` and restart it:

It will run at:
`https://0.0.0.0:8443`

Credentials are encrypted

Bettercap will not capture login data unless:
- You use `https.proxy on`
- The victim trusts Bettercap's MITM certificate
