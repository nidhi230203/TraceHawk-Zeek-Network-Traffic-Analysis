# Incident Report: TCP Port Scan Detection

## Incident Summary

| Field | Details |
|---|---|
| Incident Title | Full TCP Port Scan Detected Against Windows Target |
| Incident Category | Network Reconnaissance / Service Discovery |
| Detection Severity | High |
| Observation Date | 26 May 2026 |
| Suspected Scanner IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Detection Source | Zeek `conn.log` and Python behavioral detector |
| Validation Sources | PCAP evidence, Wireshark analysis, and Nmap output |
| MITRE ATT&CK Technique | `T1046 - Network Service Discovery` |
| Environment | Controlled Host-Only virtual lab |

## Executive Summary

A high-volume TCP port scan was detected against the Windows 11 target system during Phase 2 of the TraceHawk Network Forensics and Threat Detection Lab. The activity originated from source IP `192.168.206.128` and targeted destination IP `192.168.206.133`.

Zeek connection telemetry identified that the source contacted all `65,535` TCP destination ports on the target, generating `66,812` TCP connection observations across the full capture. A Python-based behavioral detector independently identified the activity as a high-severity TCP port scan. Within the most active rolling 300-second analysis window, the source probed `29,677` unique destination ports and generated `30,757` connections.

The observed behavior is consistent with automated network service discovery. No evidence in this investigation confirms successful exploitation or unauthorized access; however, the scan represents meaningful reconnaissance that could precede brute force activity or exploitation attempts in a real environment.

## Scope of Investigation

This investigation focused on determining whether the captured traffic represented TCP port scanning activity and documenting the supporting evidence. The analysis scope included:

- Identification of suspicious source-to-target communication patterns.
- Measurement of unique TCP destination ports contacted.
- Analysis of Zeek connection-state behavior.
- Validation using packet-level evidence and retained Nmap outputs.
- Automated alert generation using Python detection logic.
- Mapping the behavior to MITRE ATT&CK.

## Lab Environment

| System | Role | Purpose |
|---|---|---|
| Kali Linux | Simulated scanning source | Generated controlled Nmap port scan traffic |
| Windows 11 | Target system | Received TCP port probes |
| Ubuntu Linux | Monitoring node | Captured traffic and processed evidence using Zeek and Wireshark |
| Host-Only Network | Isolated test network | Contained traffic within a controlled laboratory environment |

## Evidence Collected

| Evidence Type | Repository Location | Description |
|---|---|---|
| Packet Capture | `pcaps/port-scan/port_scan.pcap` | Raw packet evidence retained for validation |
| Zeek Logs | `zeek-logs/port-scan/` | Structured traffic telemetry generated from the PCAP |
| Detection Script | `detection-scripts/port_scan_detect.py` | Python-based behavioral detector |
| CSV Alert Export | `logs/port-scan/port_scan_alerts.csv` | Structured alert evidence produced by the detector |
| Detection Output | `logs/port-scan/port_scan_detection_output.txt` | Human-readable detection result |
| Nmap Outputs | `logs/port-scan/nmap/` | Retained scan and service-verification evidence |
| Visual Evidence | `screenshots/port-scan/` | Screenshots of capture, analysis, validation, and alert output |

## Detection Methodology

The incident was identified through behavior-based network analysis. Rather than assuming that the known lab attacker was malicious, the investigation used Zeek telemetry to determine which source system displayed abnormal behavior.

The primary detection criterion was:

> A source IP contacting an unusually high number of unique TCP destination ports on the same target within a defined time period is indicative of potential TCP port scanning activity.

Zeek `conn.log` was used to identify source IP, destination IP, destination port, protocol, and connection-state information. A Python detector then evaluated source-to-target pairs using a rolling time window and raised an alert when the configured unique-port threshold was exceeded.

## Detection Results

### Full-Capture Observation

| Indicator | Result |
|---|---:|
| Suspected Scanner IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Unique TCP Destination Ports Observed | `65,535` |
| Total TCP Connections Observed | `66,812` |
| Scan Classification | Full TCP Port Scan |

The full-capture evidence establishes that the source system contacted every possible TCP destination port on the target host. This breadth of activity is a definitive indicator of automated reconnaissance.

### Peak Rolling-Window Alert

| Alert Field | Result |
|---|---:|
| Alert Severity | High |
| Rolling Analysis Window | `300 seconds` |
| Unique Ports Probed in Peak Window | `29,677` |
| Connections in Peak Window | `30,757` |
| Configured Threshold | `50 unique ports` |
| Threshold Outcome | Exceeded |
| MITRE ATT&CK Mapping | `T1046 - Network Service Discovery` |

The detector identified a concentrated period of high-volume probing in which the scanning source exceeded the configured alert threshold by a substantial margin.

## Connection-State Analysis

During the peak detection window, the Python detector recorded the following Zeek connection states:

| Connection State | Count | Interpretation |
|---|---:|---|
| `REJ` | `29,676` | The majority of probes were rejected, consistent with probing closed or non-listening ports. |
| `S0` | `1,078` | Connection attempts were observed without a completed response in the captured exchange. |
| `RSTO` | `3` | A limited number of sessions exhibited different reset behavior and required separate validation. |

The high number of rejected and incomplete sessions across a broad port range is consistent with an automated TCP scan and does not resemble normal client-to-service communication.

## Validation Activities

### Nmap Evidence

The investigation retained raw Nmap evidence for the controlled scan and subsequent service-verification activity:

| File | Purpose |
|---|---|
| `logs/port-scan/nmap/port_scan_top100.txt` | Initial targeted scan output |
| `logs/port-scan/nmap/port_scan_full_tcp.txt` | Full TCP port scan output |
| `logs/port-scan/nmap/port_scan_service_verification.txt` | Follow-up verification of responding-port candidates |

Nmap evidence was used to support the scan timeline and validate service-response observations identified during Zeek analysis.

### Wireshark Validation

Packet-level analysis was performed to validate the detection results derived from Zeek logs. The retained Wireshark evidence documents:

| Screenshot | Validation Purpose |
|---|---|
| `screenshots/port-scan/wireshark_syn_scan_analysis.png` | Demonstrates repeated SYN probes from one source to changing destination ports |
| `screenshots/port-scan/wireshark_synack_responses.png` | Demonstrates target responses associated with responding-port candidates |
| `screenshots/port-scan/wireshark_rejected_ports.png` | Demonstrates rejection/reset behavior observed during the scan |

The packet-level findings corroborate the Zeek analysis and support the determination that the traffic represented network reconnaissance.

## Indicators of Activity

| Indicator Type | Value |
|---|---|
| Suspected Source IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Protocol | TCP |
| Scan Scope | Ports `1-65535` observed |
| Behavioral Indicator | Extremely high unique destination-port count from one source to one target |
| Primary Zeek Log | `conn.log` |
| Detection Severity | High |

## MITRE ATT&CK Mapping

| Tactic | Technique | ID | Justification |
|---|---|---|---|
| Discovery | Network Service Discovery | `T1046` | The source systematically probed TCP ports on the target to determine accessible network services. |

## Impact Assessment

The investigation confirms reconnaissance activity but does not establish that the target system was compromised. Port scanning alone does not produce direct system impact; however, it provides an attacker with information about reachable services and possible attack paths.

In a production environment, this activity would be significant because it may be followed by:

- Password attacks against discovered remote access services.
- Exploitation attempts targeting exposed or outdated services.
- Lateral movement preparation.
- Asset and service enumeration within an internal network.

Given the full-port scope and sustained automated behavior, the activity was classified as a **High-severity detection event** for monitoring and investigation purposes.

## Recommended Response and Mitigation Actions

| Priority | Recommendation | Purpose |
|---:|---|---|
| 1 | Review verified responding services on the target host | Identify unnecessary exposure |
| 2 | Disable or restrict services not required for operations | Reduce attack surface |
| 3 | Restrict administrative services to approved source networks | Prevent unauthorized reconnaissance and access attempts |
| 4 | Alert on high unique destination-port counts from a single source | Improve early detection capability |
| 5 | Correlate scan alerts with authentication failures and exploit attempts | Identify escalation from reconnaissance to attack |
| 6 | Preserve PCAP, Zeek logs, and detector outputs | Support incident investigation and reporting |
| 7 | Apply host firewall and segmentation controls where appropriate | Limit unauthorized internal discovery |

## Detection Capability Assessment

| Capability | Assessment |
|---|---|
| Raw packet evidence collection | Successfully captured and preserved |
| Zeek log generation | Successfully generated structured network telemetry |
| Scanner identification without prior assumption | Successfully identified from traffic behavior |
| Full TCP scan detection | Successfully confirmed across all `65,535` ports |
| Automated behavior-based alerting | Successfully implemented using Python |
| Packet-level validation | Completed using Wireshark evidence |
| Structured alert export | Completed through CSV and text output |
| MITRE ATT&CK mapping | Completed using `T1046` |

## Evidence Index

| Evidence Artifact | Purpose |
|---|---|
| `screenshots/port-scan/traffic_visibility_test.png` | Demonstrates that monitoring visibility was validated |
| `screenshots/port-scan/nmap_portscan_test.png` | Documents initial controlled probing |
| `screenshots/port-scan/nmap_port_scan_execution.png` | Documents scan execution |
| `screenshots/port-scan/nmap_port_scan_full_execution.png` | Documents full TCP scan activity |
| `screenshots/port-scan/tcpdump_port_scan_capture.png` | Documents packet capture execution |
| `screenshots/port-scan/scanner_ip_identification.png` | Documents source identification from traffic evidence |
| `screenshots/port-scan/scanned_ports_analysis.png` | Documents destination-port analysis |
| `screenshots/port-scan/connection_state_analysis.png` | Documents connection-state findings |
| `screenshots/port-scan/responding_ports_candidates.png` | Documents candidate response behavior |
| `screenshots/port-scan/nmap_service_verification.png` | Documents service validation evidence |
| `screenshots/port-scan/wireshark_syn_scan_analysis.png` | Documents repeated SYN activity |
| `screenshots/port-scan/wireshark_synack_responses.png` | Documents target response evidence |
| `screenshots/port-scan/wireshark_rejected_ports.png` | Documents rejection/reset behavior |
| `screenshots/port-scan/python_peak_window_detection.png` | Documents automated detection in the peak analysis window |
| `screenshots/port-scan/python_port_scan_alert.png` | Documents the primary alert result |

## Analyst Conclusion

The investigation confirmed a high-volume full TCP port scan against the Windows 11 target system. Analysis of Zeek `conn.log` identified `192.168.206.128` as the suspicious source after it probed `192.168.206.133` across all `65,535` TCP destination ports, generating `66,812` observed TCP connections. Python-based rolling-window detection raised a High-severity alert after observing `29,677` unique port probes and `30,757` connections in the most active five-minute period. Nmap evidence and Wireshark packet analysis supported the conclusion that the activity represented automated service discovery.

No evidence in this investigation confirms successful exploitation or unauthorized access. The event is documented as reconnaissance activity mapped to MITRE ATT&CK technique `T1046 - Network Service Discovery`. This incident demonstrates practical SOC investigation skills including traffic collection, Zeek analysis, evidence-based source identification, packet validation, behavioral detection, alert evidence export, and professional incident documentation.
