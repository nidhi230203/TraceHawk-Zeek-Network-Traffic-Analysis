# DNS Anomaly Analysis — Phase 3

## Objective

This phase investigates a DNS query pattern that resembles DNS tunneling or encoded-query activity. The purpose was to compare ordinary DNS resolution with an unusual burst of unique subdomain queries, identify the suspicious source from captured evidence, and test whether the behaviour could be detected automatically from Zeek `dns.log`.

This activity was performed inside an isolated lab network. The finding is recorded as a **DNS tunneling-like anomaly**; it does not claim that data exfiltration occurred.

## Lab Context

| System | Role | Address Observed in Evidence |
|---|---|---|
| Kali Linux | DNS query source identified during analysis | `192.168.206.128` |
| Ubuntu Linux | Controlled DNS resolver and monitoring system | `192.168.206.131` |
| Controlled Domain | Domain used for baseline and anomaly queries | `lab.test` |

## Evidence Used

| Evidence Type | Repository Path | Purpose |
|---|---|---|
| Packet capture | `pcaps/dns-anomaly/dns_anomaly.pcap` | Raw DNS traffic evidence |
| Zeek DNS log | `zeek-logs/dns-anomaly/dns.log` | Main source for query-level analysis |
| Supporting Zeek logs | `zeek-logs/dns-anomaly/conn.log`, `packet_filter.log` | Network and capture context |
| Detector script | `detection-scripts/dns_anomaly_detect.py` | Automated anomaly detection |
| Detector output | `logs/dns-anomaly/dns_anomaly_detection_output.txt` | Preserved alert result |
| Alert CSV | `logs/dns-anomaly/dns_anomaly_alerts.csv` | Structured alert evidence |
| Query-generation files | `logs/dns-anomaly/query-generation/` | Baseline and suspicious query records |
| Screenshots | `screenshots/dns-anomaly/` | Visual investigation evidence |

## Baseline Activity

A short baseline was generated before the anomalous query burst. It used readable, repeating hostnames under the controlled domain:

```text
portal.lab.test
mail.lab.test
update.lab.test
portal.lab.test
mail.lab.test
```

This baseline represented normal low-volume DNS behaviour: only five lookups and three unique names.

Evidence:

- [`baseline_dns_queries.png`](../screenshots/dns-anomaly/baseline_dns_queries.png)
- [`dns_client_resolution_validation.png`](../screenshots/dns-anomaly/dns_client_resolution_validation.png)
- [`dns_resolver_query_log.png`](../screenshots/dns-anomaly/dns_resolver_query_log.png)
- [`baseline_dns_queries.txt`](../logs/dns-anomaly/query-generation/baseline_dns_queries.txt)

## Suspicious Query Pattern

The anomaly traffic consisted of rapidly generated, unique subdomain queries under the same parent domain. The query format included a `chunk` prefix and a long changing value, for example:

```text
chunk001-fa48194fbdea9ace20175e13.lab.test
chunk002-6cf8be4c3e0f13c7ab44a806.lab.test
chunk003-15cd95ac4f805c1f512830e2.lab.test
```

Unlike the baseline, these queries were unique and used long labels that resemble chunked or encoded DNS traffic. This behaviour is a useful detection signal for DNS tunneling-like activity.

Evidence:

- [`dns_anomaly_resolver_log.png`](../screenshots/dns-anomaly/dns_anomaly_resolver_log.png)
- [`dns_anomaly_pcap_filtered_traffic.png`](../screenshots/dns-anomaly/dns_anomaly_pcap_filtered_traffic.png)
- [`suspicious_dns_queries.txt`](../logs/dns-anomaly/query-generation/suspicious_dns_queries.txt)

## Packet Capture and Zeek Review

The traffic was captured on the Ubuntu monitoring system and processed with Zeek. Review of `dns.log` showed the baseline requests followed by the long `chunk...lab.test` queries from the same source to the same DNS resolver.

| Observed Field | Result |
|---|---|
| DNS query source | `192.168.206.128` |
| DNS resolver destination | `192.168.206.131` |
| Domain analysed | `lab.test` |
| Query type | `A` |
| Response result | `NOERROR` |

Evidence:

- [`dns_pcap_initial_validation.png`](../screenshots/dns-anomaly/dns_pcap_initial_validation.png)
- [`tcpdump_dns_capture_started.png`](../screenshots/dns-anomaly/tcpdump_dns_capture_started.png)
- [`tcpdump_dns_capture_completed.png`](../screenshots/dns-anomaly/tcpdump_dns_capture_completed.png)
- [`zeek_dns_logs_generated.png`](../screenshots/dns-anomaly/zeek_dns_logs_generated.png)
- [`zeek_dns_query_analysis.png`](../screenshots/dns-anomaly/zeek_dns_query_analysis.png)

## Query Volume Findings

Zeek analysis and the Python detector established the following behaviour:

| Finding | Result |
|---|---:|
| Total DNS queries from suspected source | `255` |
| Unique queried domains | `253` |
| Suspicious long-label queries | `250` |
| Unique suspicious subdomains | `250` |
| Suspicious query ratio | `98.04%` |

The contrast is clear: five simple baseline queries were followed by 250 unique, long-label DNS requests. Almost all queries in the analysed window matched the suspicious pattern.

## Automated Detection Result

A Python detector was used to analyse the Zeek DNS log without hardcoding the source host. It evaluates query behaviour per source and resolver, identifies unique long/high-entropy subdomains within a rolling time window, and exports the alert as both text and CSV evidence.

| Alert Field | Result |
|---|---|
| Alert | Suspicious DNS Unique-Subdomain Burst Detected |
| Severity | High |
| Suspected DNS Source IP | `192.168.206.128` |
| DNS Resolver IP | `192.168.206.131` |
| Base Domain Analysed | `lab.test` |
| Total Queries in Peak Window | `255` |
| Unique Queries in Peak Window | `253` |
| Suspicious Long-Label Queries | `250` |
| Unique Suspicious Subdomains | `250` |
| Suspicious Query Ratio | `98.04%` |
| Threshold | `50` unique suspicious subdomains |
| Rolling Analysis Window | `300 seconds` |
| Peak Window Duration | `138.21 seconds` |
| DNS Response Codes | `NOERROR=255` |

Evidence:

- [`dns_anomaly_detect.py`](../detection-scripts/dns_anomaly_detect.py)
- [`dns_anomaly_detection_output.txt`](../logs/dns-anomaly/dns_anomaly_detection_output.txt)
- [`dns_anomaly_alerts.csv`](../logs/dns-anomaly/dns_anomaly_alerts.csv)
- [`python_dns_anomaly_alert.png`](../screenshots/dns-anomaly/python_dns_anomaly_alert.png)

## Why This Was Flagged

| Behaviour | Analyst Interpretation |
|---|---|
| `250` unique suspicious subdomains | Unusually high subdomain diversity from one source |
| Long, changing labels | Consistent with encoded or chunked query patterns |
| `98.04%` suspicious query ratio | Anomalous traffic dominated the analysis window |
| Burst completed in `138.21` seconds | Indicates automated activity rather than occasional name resolution |
| `NOERROR=255` | Resolver successfully responded to the generated queries |

## ATT&CK Reference

| Reference | Technique | Use in This Case |
|---|---|---|
| `T1048.003` | Exfiltration Over Alternative Protocol: DNS | Behavioural reference for DNS tunneling-like query patterns |

The mapping is used as a detection reference. This lab demonstrates the observable DNS pattern associated with tunneling-like behaviour; it does not demonstrate real information leaving an organisation.

## Analyst Assessment

The evidence identifies `192.168.206.128` as the source of a high-volume DNS anomaly directed to resolver `192.168.206.131`. The activity differed significantly from the baseline: readable repeated names were replaced by 250 unique long-label requests under `lab.test`. The pattern was visible in the PCAP, recorded in Zeek DNS telemetry, and detected successfully by the Python rule.

The event is assessed as a **High-severity DNS tunneling-like anomaly** in the context of this lab. No compromise or data exfiltration is claimed.

## Recommended Investigation Actions

In a production environment, similar activity should lead to:

- review of the host producing large numbers of unique subdomains;
- examination of long and high-entropy DNS query labels;
- correlation with endpoint, proxy, authentication, and data-access logs;
- validation of whether the parent domain is expected for the environment;
- preservation of DNS logs and packet captures before containment decisions.

## Conclusion

Phase 3 demonstrates a practical DNS-focused investigation workflow: baseline validation, anomaly generation, packet capture, Zeek DNS analysis, behaviour-based detection, and evidence preservation. The findings show how suspicious DNS query behaviour can be identified without assuming the source in advance and without overstating the impact of the detected activity.
