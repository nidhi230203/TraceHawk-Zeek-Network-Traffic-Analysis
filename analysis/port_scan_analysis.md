# TCP Port Scan Detection Analysis

## Overview

This document presents the analysis of a TCP port scan captured during Phase 2 of the TraceHawk Network Forensics and Threat Detection Lab. The investigation was performed in a controlled virtual environment and focused on identifying network reconnaissance activity through packet capture, Zeek telemetry, Wireshark validation, Nmap evidence, and Python-based behavioral detection.

The suspected scanning source was not treated as known in advance. It was identified from network evidence after a single source IP generated an abnormally high number of TCP connection attempts across unique destination ports on one target host.

## Investigation Objective

The objective of this phase was to detect and investigate TCP port scanning activity against the Windows target system by answering the following analyst questions:

- Which source IP generated the scanning activity?
- Which host was targeted?
- How broad and aggressive was the scan?
- What connection-state pattern was observed in Zeek telemetry?
- Was the behavior validated through packet-level and service-verification evidence?
- Could the activity be detected automatically through a reusable Python rule?

## Lab Context

| Component | Role | Details |
|---|---|---|
| Kali Linux | Simulated scanning source | Executed Nmap reconnaissance activity |
| Windows 11 | Target system | Host subjected to TCP port probing |
| Ubuntu Linux | Monitoring node | Captured traffic and processed PCAP data using Zeek |
| Network | Test environment | Isolated Host-Only virtual network |

## Evidence Sources

| Evidence Type | Repository Location | Investigation Value |
|---|---|---|
| Packet capture | `pcaps/port-scan/port_scan.pcap` | Raw network evidence of the scan |
| Zeek connection log | `zeek-logs/port-scan/conn.log` | Source, target, destination port, protocol, and connection-state telemetry |
| Supporting Zeek logs | `zeek-logs/port-scan/` | Additional network activity recorded during the capture |
| Python detector | `detection-scripts/port_scan_detect.py` | Automated behavior-based detection logic |
| Alert export | `logs/port-scan/port_scan_alerts.csv` | Structured detector evidence |
| Detection output | `logs/port-scan/port_scan_detection_output.txt` | Human-readable alert evidence |
| Nmap evidence | `logs/port-scan/nmap/` | Raw scan and service-verification outputs |
| Screenshots | `screenshots/port-scan/` | Visual evidence supporting each investigation stage |

## Analysis Workflow

The investigation followed a SOC-style workflow:

`Traffic Visibility Validation -> Packet Capture -> Port Scan Simulation -> Zeek Log Generation -> Scanner Identification -> Connection-State Analysis -> Service and Packet Validation -> Automated Detection -> Documentation`

## Traffic Collection and Zeek Processing

Traffic generated during the controlled scan was captured from the monitoring node and preserved as a PCAP file. The PCAP was processed using Zeek to generate structured logs suitable for investigation.

The principal detection source was `conn.log`. A TCP port scan is characterized by a source system attempting connections to a broad set of destination ports on a target system; `conn.log` provides the fields required to identify this behavior.

## Scanner Identification from Zeek Logs

Frequency-based analysis of `conn.log` identified one source-to-target pair with activity spanning the full TCP port range.

| Finding | Observed Value |
|---|---|
| Suspected Scanner IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Total Unique TCP Ports Observed | `65,535` |
| Total TCP Connections Observed | `66,812` |
| Detected Activity | Full TCP Port Scan |

The source IP was classified as suspicious because it contacted the same target across `65,535` unique TCP destination ports. This behavior is not consistent with normal user or application activity and confirms automated network service discovery.

## Peak-Window Detection Analysis

A Python detector evaluated the Zeek connection telemetry using a rolling time window. The detector identified the highest concentration of suspicious probing activity within a 300-second period.

| Detection Field | Observed Value |
|---|---|
| Severity | High |
| Suspected Scanner IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Rolling Analysis Window | `300 seconds` |
| Unique Ports Probed in Peak Window | `29,677` |
| Connections in Peak Window | `30,757` |
| Configured Threshold | `50 unique ports` |
| MITRE ATT&CK Mapping | `T1046 - Network Service Discovery` |

The detection threshold was exceeded by a substantial margin. Even within a five-minute period, the source probed tens of thousands of unique destination ports, confirming high-volume automated scanning.

## Connection-State Analysis

The detector summarized connection states observed during the peak detection window.

| Zeek Connection State | Count | Analyst Interpretation |
|---|---:|---|
| `REJ` | `29,676` | Most probes were rejected by the target, consistent with closed or non-listening ports. |
| `S0` | `1,078` | Connection attempts were observed without a complete response in the captured exchange. |
| `RSTO` | `3` | A small subset showed different reset behavior and was retained for service and packet validation. |

The dominance of rejected and incomplete connections, combined with a very high unique-port count, is consistent with automated reconnaissance rather than legitimate application communication.

## Responding-Port Candidate Review

The investigation extracted ports showing response behavior that differed from the dominant rejected-port pattern. These ports were treated as responding-port candidates until reviewed using Nmap service verification and Wireshark packet evidence.

The supporting evidence is retained in:

- `screenshots/port-scan/responding_ports_candidates.png`
- `screenshots/port-scan/nmap_service_verification.png`
- `logs/port-scan/nmap/port_scan_service_verification.txt`

This approach avoids overstating findings. Ports are documented as confirmed open services only when supported by the retained Nmap or packet-level evidence.

## Packet-Level Validation

Wireshark was used to validate the Zeek-based findings directly within the packet capture. Packet inspection confirmed the expected TCP scan pattern: repeated SYN probes from a single source toward the same target while destination ports changed rapidly.

| Screenshot | Purpose |
|---|---|
| `wireshark_syn_scan_analysis.png` | Shows repeated SYN probes across changing destination ports |
| `wireshark_synack_responses.png` | Preserves target response evidence associated with responding ports |
| `wireshark_rejected_ports.png` | Preserves rejected/reset response evidence associated with non-listening ports |

The Wireshark validation supports the Zeek conclusion that the activity was automated port scanning rather than normal service usage.

## Automated Detection Logic

The Python detector was created to identify suspicious network behavior from Zeek `conn.log` without hardcoding an attacker IP. The script groups TCP activity by source and target, evaluates the number of unique destination ports contacted within a rolling time window, classifies severity, maps the result to MITRE ATT&CK, and exports alert evidence.

The detection rule is:

> Alert when a single source-to-target pair exceeds the configured threshold of unique TCP destination ports within the rolling analysis window.

The detector produced a high-severity finding for `192.168.206.128` targeting `192.168.206.133`, based on `29,677` unique TCP ports in the peak five-minute window and `65,535` unique TCP ports across the complete capture.

## Findings Summary

| Attribute | Result |
|---|---|
| Incident Type | TCP Port Scan |
| Scan Scope | Full TCP port range observed |
| Suspected Scanner IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Total Unique Ports Probed | `65,535` |
| Total Connections Observed | `66,812` |
| Peak Five-Minute Unique-Port Count | `29,677` |
| Peak Five-Minute Connection Count | `30,757` |
| Peak Window States | `REJ=29,676`, `S0=1,078`, `RSTO=3` |
| Severity | High |
| Detection Source | Zeek `conn.log` and Python detector |
| Validation Sources | PCAP, Wireshark, and Nmap evidence |
| MITRE ATT&CK Technique | `T1046 - Network Service Discovery` |

## MITRE ATT&CK Mapping

| Tactic | Technique | Technique ID | Relevance |
|---|---|---|---|
| Discovery | Network Service Discovery | `T1046` | The source probed a broad TCP port range on the target to discover accessible network services. |

## Risk and Impact Assessment

A port scan does not by itself confirm system compromise. However, a full TCP scan is a significant reconnaissance indicator because it can reveal remotely accessible services that may later be targeted for credential attacks or exploitation.

This activity is assessed as High severity for detection and investigation purposes because:

- All `65,535` TCP destination ports were probed.
- The activity was automated and sustained.
- One source targeted one asset at high volume.
- The scan may represent preparation for follow-on attacks.

## Recommended Defensive Actions

- Review verified responding services on the target and disable unnecessary exposure.
- Restrict remote administrative services to trusted network segments.
- Configure detection alerts for high unique destination-port counts from a single source.
- Correlate scan findings with subsequent authentication attacks or exploitation attempts.
- Preserve Zeek logs, PCAP evidence, detector outputs, and verification results for incident reconstruction.
- Apply segmentation, host firewall controls, or rate-limiting controls where appropriate.

## Evidence Index

| Evidence File | Purpose |
|---|---|
| `screenshots/port-scan/traffic_visibility_test.png` | Confirms visibility of test traffic before the full capture |
| `screenshots/port-scan/nmap_portscan_test.png` | Initial controlled probe evidence |
| `screenshots/port-scan/nmap_port_scan_execution.png` | Port scan execution evidence |
| `screenshots/port-scan/nmap_port_scan_full_execution.png` | Full TCP scan execution evidence |
| `screenshots/port-scan/tcpdump_port_scan_capture.png` | Packet-capture evidence |
| `screenshots/port-scan/scanner_ip_identification.png` | Zeek-based suspicious source identification |
| `screenshots/port-scan/scanned_ports_analysis.png` | Destination-port and state-analysis evidence |
| `screenshots/port-scan/connection_state_analysis.png` | Zeek connection-state analysis evidence |
| `screenshots/port-scan/responding_ports_candidates.png` | Candidate responding-port evidence |
| `screenshots/port-scan/nmap_service_verification.png` | Service-verification evidence |
| `screenshots/port-scan/wireshark_syn_scan_analysis.png` | Packet-level scan pattern evidence |
| `screenshots/port-scan/wireshark_synack_responses.png` | Packet-level target response evidence |
| `screenshots/port-scan/wireshark_rejected_ports.png` | Packet-level rejected-port evidence |
| `screenshots/port-scan/python_peak_window_detection.png` | Automated rolling-window detection evidence |
| `screenshots/port-scan/python_port_scan_alert.png` | Primary Python alert screenshot |

## Analyst Conclusion

The investigation confirmed a full TCP port scan against the Windows target system. Zeek telemetry identified `192.168.206.128` as the suspicious source after it contacted `192.168.206.133` across all `65,535` TCP destination ports. Python-based rolling-window analysis detected a high-severity concentration of `29,677` unique destination-port probes within a five-minute window. The findings were supported by retained Nmap evidence and Wireshark packet-level validation.

This phase demonstrates practical SOC capabilities in packet capture, Zeek log analysis, evidence-based source identification, connection-state interpretation, packet validation, behavior-based detection engineering, MITRE ATT&CK mapping, and structured incident documentation.
