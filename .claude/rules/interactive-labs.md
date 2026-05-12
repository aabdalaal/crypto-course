---
description: All 10 interactive labs — labIds, modules, purpose, and the hard PR8 constraint that no lab may make server calls
alwaysApply: true
---

All labs use the **Web Crypto API** for on-device computation. **No lab makes server calls.** This is a hard compliance requirement (PR8).

| `labId` | Module | Purpose |
|---------|--------|---------|
| `hash_lab` | 0, 6 | SHA-256 integrity verification |
| `vigenere_lab` | 1 | Vigenère cipher encrypt/decrypt |
| `openssl_sym_lab` | 2 | Symmetric encryption demo |
| `openssl_modes_lab` | 3 | AES ECB/CBC/CTR/GCM — 4-tab |
| `openssl_hash_lab` | 4 | SHA hash, avalanche, HMAC, chain — 4-tab |
| `openssl_rsa_lab` | 5, 7 | RSA keygen, encryption, compare, signatures — 4-tab |
| `cert_lab` | 8 | X.509 inspect, CSR, chain — 3-tab |
| `sign_lab` | 9, 10, 13 | Digital signature sign/verify |
| `ecdh_lab` | 11 | ECDH key exchange |
| `attacks_lab` | 12 | Timing attack + integer factorisation — 2-tab |

Multi-tab labs use `set{Lab}Tab(tab)` functions: `setHashTab`, `setRSATab`, `setModesTab`, `setCertTab`, `setAtkTab`.
