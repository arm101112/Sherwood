# Security

This repository contains trading infrastructure. Treat all credentials,
API keys, and broker configuration as highly sensitive.

- Never commit `.env` files or any file containing real credentials
- Rotate API keys immediately if accidentally exposed
- All broker connections use TLS; do not disable certificate verification
- Paper trading mode is the default; live mode requires explicit configuration

For security issues, contact the maintainers privately before disclosing publicly.
