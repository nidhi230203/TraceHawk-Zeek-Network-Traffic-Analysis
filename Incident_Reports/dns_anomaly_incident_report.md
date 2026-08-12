# Incident Report: Suspicious DNS Unique-Subdomain Burst

## Incident Summary

| Field | Detail |
|---|---|
| Incident Title | Suspicious DNS Unique-Subdomain Burst Detected |
| Incident Category | DNS Anomaly / DNS Tunneling-Like Behaviour |
| Severity | High |
| Lab Phase | Phase 3 — DNS Anomaly Detection |
| Suspected DNS Source IP | `192.168.206.128` |
| DNS Resolver IP | `192.168.206.131` |
| Analysed Domain | `lab.test` |
| Primary Data Source | Zeek `dns.log` |
| Detection Method | Python behavioural detector using unique long-label query analysis |
| ATT&CK Reference | `T1048.003 - Exfiltration Over Alternative Protocol: DNS` |
| Classification Note | DNS tunneling-like anomaly; exfiltration not confirmed |

## Executive Summary

During Phase 3 of the TraceHawk lab, a high-volume DNS anomaly was observed from source IP `192.168.206.128` to the controlled DNS resolver at `192.168.206.131`. The activity began with a small normal baseline consisting of readable DNS names under `lab.test`, followed by a rapid burst of long, unique `chunk...lab.test` queries.

Zeek DNS telemetry recorded `255` DNS queries in the analysed window, of which `253` were unique. The detector classified `250` of these requests as suspicious long-label subdomains, resulting in a suspicious-query ratio of `98.04%`. The burst occurred over `138.21` seconds and triggered a High-severity alert.

The evidence supports a DNS tunneling-like query pattern in the controlled lab. This report does not claim that information was actually exfiltrated or that the monitored system was compromised.

## Investigation Scope

The investigation was performed to determine:

- whether DNS traffic differed materially from normal baseline resolution;
- which source generated the suspicious query burst;
- whether the queries displayed characteristics commonly associated with DNS tunneling-like behaviour;
- whether the behaviour could be detected automatically from Zeek telemetry;
- which evidence should be retained for reporting and future correlation.

## Lab Environment

| Component | Role in Investigation |
|---|---|
| Kali Linux | Generated controlled DNS baseline and anomaly traffic |
| Ubuntu Linux | Hosted the controlled DNS resolver, captured traffic, and generated Zeek logs |
| Controlled Domain | `lab.test` |
| Network | Isolated virtual lab environment |

## Evidence Inventory

| Artifact | Repository Path | Purpose |
|---|---|---|
| DNS packet capture | [`pcaps/dns-anomaly/dns_anomaly.pcap`](../pcaps/dns-anomaly/dns_anomaly.pcap) | Raw traffic evidence |
| Zeek DNS log | [`zeek-logs/dns-anomaly/dns.log`](../zeek-logs/dns-anomaly/dns.log) | Primary query-level telemetry |
| Zeek connection log | [`zeek-logs/dns-anomaly/conn.log`](../zeek-logs/dns-anomaly/conn.log) | Supporting connection context |
| Detector script | [`detection-scripts/dns_anomaly_detect.py`](../detection-scripts/dns_anomaly_detect.py) | Automated anomaly-detection logic |
| Detector text output | [`logs/dns-anomaly/dns_anomaly_detection_output.txt`](../logs/dns-anomaly/dns_anomaly_detection_output.txt) | Preserved alert output |
| Detector CSV output | [`logs/dns-anomaly/dns_anomaly_alerts.csv`](../logs/dns-anomaly/dns_anomaly_alerts.csv) | Structured alert evidence |
| Baseline query record | [`logs/dns-anomaly/query-generation/baseline_dns_queries.txt`](../logs/dns-anomaly/query-generation/baseline_dns_queries.txt) | Record of normal comparison traffic |
| Suspicious query record | [`logs/dns-anomaly/query-generation/suspicious_dns_queries.txt`](../logs/dns-anomaly/query-generation/suspicious_dns_queries.txt) | Record of anomalous generated names |
| Technical analysis | [`analysis/dns_anomaly_analysis.md`](../analysis/dns_anomaly_analysis.md) | Detailed analyst review |

## Investigation Timeline

| Stage | Activity | Outcome |
|---|---|---|
| Resolver Validation | Confirmed controlled DNS response for `portal.lab.test` | Query path and resolver operation verified |
| Baseline Collection | Sent five short readable DNS queries | Established low-volume normal comparison pattern |
| Anomaly Generation | Sent unique long `chunk...lab.test` DNS queries | Created a controlled suspicious query burst |
| Packet Capture | Captured DNS activity for review | `dns_anomaly.pcap` preserved |
| Zeek Processing | Processed captured traffic into structured logs | `dns.log` generated for analysis |
| Query Review | Examined source, resolver, names, query type and result | Suspicious source and pattern identified |
| Automated Detection | Ran Python detector against `dns.log` | High-severity alert exported as text and CSV |

## Baseline Versus Anomalous Behaviour

The baseline included a small number of repeated and readable requests:

```text
portal.lab.test
mail.lab.test
update.lab.test
portal.lab.test
mail.lab.test
```

The later activity used unique, long labels such as:

```text
chunk001-fa48194fbdea9ace20175e13.lab.test
chunk002-6cf8be4c3e0f13c7ab44a806.lab.test
chunk003-15cd95ac4f805c1f512830e2.lab.test
```

| Comparison Point | Baseline Behaviour | Suspicious Behaviour |
|---|---|---|
| Naming Pattern | Short readable names | Long changing `chunk` labels |
| Query Volume | Low | High-volume burst |
| Repetition | Repeated lookups present | Nearly all names unique |
| Analyst Interpretation | Expected test resolution | DNS tunneling-like anomaly indicator |

## Detection Findings

| Finding | Observed Result |
|---|---:|
| Suspected DNS Source IP | `192.168.206.128` |
| DNS Resolver IP | `192.168.206.131` |
| Base Domain Analysed | `lab.test` |
| Total Queries in Peak Window | `255` |
| Unique Queries in Peak Window | `253` |
| Suspicious Long-Label Queries | `250` |
| Unique Suspicious Subdomains | `250` |
| Suspicious Query Ratio | `98.04%` |
| Rolling Analysis Window | `300 seconds` |
| Peak Window Duration | `138.21 seconds` |
| DNS Response Codes | `NOERROR=255` |
| Alert Severity | High |

## Detection Logic

The Python detector reviewed Zeek DNS telemetry by source and resolver pair. It evaluated the number of unique subdomains within a rolling window and treated long, high-entropy labels as suspicious indicators.

The alert was triggered because the source generated `250` unique suspicious subdomains, exceeding the configured threshold of `50`. The alert is based on observable DNS behaviour rather than on a pre-labelled attacker address.

## Evidence Validation

### Resolver and Baseline Validation

The controlled resolver returned the configured response for the baseline lookup, confirming that the DNS path was functioning before anomaly generation.

Evidence:

- [`dns_client_resolution_validation.png`](../screenshots/dns-anomaly/dns_client_resolution_validation.png)
- [`dns_resolver_query_log.png`](../screenshots/dns-anomaly/dns_resolver_query_log.png)
- [`baseline_dns_queries.png`](../screenshots/dns-anomaly/baseline_dns_queries.png)

### Packet Capture Validation

The packet capture preserved both baseline traffic and the later anomaly sequence. Filtered PCAP review showed DNS requests from `192.168.206.128` to `192.168.206.131` for the changing `chunk...lab.test` names.

Evidence:

- [`tcpdump_dns_capture_started.png`](../screenshots/dns-anomaly/tcpdump_dns_capture_started.png)
- [`tcpdump_dns_capture_completed.png`](../screenshots/dns-anomaly/tcpdump_dns_capture_completed.png)
- [`dns_pcap_initial_validation.png`](../screenshots/dns-anomaly/dns_pcap_initial_validation.png)
- [`dns_anomaly_pcap_filtered_traffic.png`](../screenshots/dns-anomaly/dns_anomaly_pcap_filtered_traffic.png)

### Zeek and Detector Validation

Zeek `dns.log` showed the normal names followed by long `chunk`-style names from the same source. The Python detector converted those observations into a structured High-severity alert.

Evidence:

- [`zeek_dns_logs_generated.png`](../screenshots/dns-anomaly/zeek_dns_logs_generated.png)
- [`zeek_dns_query_analysis.png`](../screenshots/dns-anomaly/zeek_dns_query_analysis.png)
- [`python_dns_anomaly_alert.png`](../screenshots/dns-anomaly/python_dns_anomaly_alert.png)

## ATT&CK Reference

| Tactic Context | Technique | Technique ID | Relevance |
|---|---|---|---|
| Exfiltration | Exfiltration Over Alternative Protocol: DNS | `T1048.003` | The observed high-volume, unique subdomain pattern resembles DNS-based transfer behaviour. |

This mapping is used as a behavioural reference for detection. The lab demonstrates a DNS tunneling-like pattern; it does not prove actual data loss.

## Impact Assessment

No compromise or confirmed exfiltration was established during this investigation. The detected activity is still important because, in a real environment, similar DNS behaviour could indicate a host attempting to communicate through covert DNS channels or encode information into subdomain lookups.

The event is classified as High severity in this lab because:

- one source produced a concentrated query burst;
- `250` unique suspicious subdomains were generated;
- anomalous requests formed `98.04%` of queries in the peak window;
- the pattern was automated and strongly distinct from the baseline.

## Recommended Response Actions

| Priority | Recommendation | Purpose |
|---:|---|---|
| 1 | Investigate the host generating high-volume unique DNS labels | Determine whether the process is legitimate or malicious |
| 2 | Review the queried parent domain and resolver path | Validate whether DNS destinations are expected |
| 3 | Correlate with endpoint, proxy, authentication and data-access events | Determine whether DNS activity is linked to broader compromise |
| 4 | Alert on bursts of unique, long or high-entropy DNS subdomains | Improve early detection of similar patterns |
| 5 | Preserve DNS telemetry and PCAP evidence | Support timeline reconstruction and response decisions |
| 6 | Apply containment only after validation in production incidents | Avoid disrupting legitimate DNS-heavy services without evidence |

## Analyst Conclusion

The investigation identified a High-severity DNS tunneling-like anomaly from `192.168.206.128` to the controlled resolver at `192.168.206.131`. The source generated `255` DNS queries, including `250` unique suspicious long-label subdomains under `lab.test`, within a short burst lasting `138.21` seconds. Zeek analysis and the Python detector independently supported the finding, while packet-capture and screenshot evidence preserved the observable behaviour.

The incident is documented as suspicious DNS query activity aligned with `T1048.003 - Exfiltration Over Alternative Protocol: DNS`. The evidence confirms the anomalous pattern, but does not establish successful exfiltration or target compromise.
