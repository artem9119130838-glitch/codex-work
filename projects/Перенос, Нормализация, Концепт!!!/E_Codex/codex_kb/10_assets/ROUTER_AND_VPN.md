# Asset: Router and VPN

## Router

- Router: Keenetic Hero 4G
- Used for DNS routing and VPN-related traffic policies.

## WireGuard server

- Server public IP: `109.248.170.181`
- Interface: `wg0`
- VPN network: `10.10.0.0/24`
- Server VPN IP: `10.10.0.1`
- UDP port: `51820`

## 1C VPN model

Target:

- one WireGuard profile per user/device;
- 1C clients connect to `10.10.0.1`;
- public 1C ports `1540-1591` closed after VPN validation.

For 1C-only access:

```ini
AllowedIPs = 10.10.0.0/24
```

## Amnezia / EE / external VPN routing

Observed older endpoint:

```text
185.155.99.161:9455
```

Observed DNS:

```text
100.64.0.1
8.8.4.4
```

Full tunnel configs used:

```ini
AllowedIPs = 0.0.0.0/0, ::/0
```

## Gemini / Google routing

Recommended narrow DNS route list:

```text
gemini.google.com
aistudio.google.com
generativelanguage.googleapis.com
ai.google.dev
alkalimakersuite-pa.clients6.google.com
makersuite.google.com
```

Avoid broad Google routing unless needed:

```text
google.com
clients6.google.com
content.googleapis.com
onegoogle.com
ogs.google.com
labs.google.com
```

## Known pitfalls

- Broad Google IP routes can break targeted Gemini routing.
- Do not manually force Windows DNS to `10.10.0.1` unless that is the explicit design.
- Browser Secure DNS / DoH can bypass router logic.
- Android Private DNS can bypass router logic.
- Reusing one WireGuard profile on multiple devices causes unstable behavior.
