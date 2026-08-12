# Incident Report: SSH Brute Force Activity Against Windows Host

## Incident Summary

| Field | Detail |
|---|---|
| Incident Title | Automated SSH Brute Force Activity Detected Against Windows Host |
| Incident Category | Credential Attack / Repeated SSH Authentication Attempts |
| Severity | High |
| Lab Phase | Phase 1 — SSH Brute Force Detection |
| Suspected Source IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Target Service | `22/tcp` — SSH |
| Confirmed Exposed Service | OpenSSH on port `22/tcp` |
| Primary Evidence Source | Zeek `conn.log` and preserved packet capture |
| Detection Method | Connection-frequency based Python detector |
| ATT&CK Mapping | `T1110 - Brute Force` |
| Environment | Isolated virtual lab network |

## Executive Summary

A high-volume SSH brute force pattern was observed against the Windows target host at `192.168.206.133`. Initial service verification confirmed that SSH was exposed on TCP port `22`. A controlled Hydra password-guessing operation was then directed at the SSH service from source IP `192.168.206.128`, using the username `testuser` and a password wordlist.

Traffic collection and Zeek analysis identified `192.168.206.128` as the dominant source of SSH connections to the target. The retained Zeek evidence shows `2,225` source-to-target connections associated with TCP port `22`, of which `2,223` were classified with the `ssh` service. A Python detector independently raised an alert for possible SSH brute force activity involving the same source and destination pair.

The evidence confirms repeated automated SSH connection activity consistent with brute force testing. This report does not claim a successful login or compromise of the target system because successful authentication was not established by the retained evidence.

## Scope of Investigation

The investigation focused on:

- validating reachability between the simulated source and the Windows target;
- confirming that the SSH service was available on the target host;
- capturing the network traffic generated during controlled password-guessing activity;
- identifying the suspicious source through Zeek connection evidence;
- validating the SSH traffic pattern through Wireshark;
- documenting the Python detector alert and mapping the activity to ATT&CK.

## Environment and Systems

| Component | Role in Investigation |
|---|---|
| Kali Linux | Generated controlled Hydra SSH authentication attempts |
| Windows 11 | Hosted the SSH service targeted during testing |
| Ubuntu Linux | Captured traffic and generated Zeek network logs |
| Network | Controlled virtual lab segment used for safe testing |

## Evidence Inventory

| Artifact | Repository Path | Purpose |
|---|---|---|
| PCAP Evidence | [`pcaps/ssh_bruteforce.pcap`](../pcaps/ssh_bruteforce.pcap) | Packet-level evidence from the SSH activity |
| Zeek Connection Log | [`zeek-logs/ssh-bruteforce/conn.log`](../zeek-logs/ssh-bruteforce/conn.log) | Source-to-target SSH connection analysis |
| Zeek SSH Log | [`zeek-logs/ssh-bruteforce/ssh.log`](../zeek-logs/ssh-bruteforce/ssh.log) | SSH protocol telemetry retained for review |
| Detector Script | [`detection-scripts/detect_ssh_bruteforce.py`](../detection-scripts/detect_ssh_bruteforce.py) | Automated high-frequency SSH activity detector |
| Technical Analysis | [`analysis/brute_force_analysis.md`](../analysis/brute_force_analysis.md) | Phase 1 analysis notes |
| Screenshots | [`screenshots/ssh-bruteforce/`](../screenshots/ssh-bruteforce/) | Visual evidence of setup, capture, analysis and alerting |

## Investigation Timeline

| Stage | Activity | Result |
|---|---|---|
| Connectivity Validation | Kali host tested reachability to the Windows target | Target `192.168.206.133` reachable from source environment |
| Service Verification | Nmap check performed against TCP port `22` | SSH service confirmed open on the target |
| Capture Start | Ubuntu monitoring node started `tcpdump` capture | Packet collection initiated before attack traffic |
| Controlled Attack Simulation | Hydra generated SSH password-guessing attempts against `testuser` | High-frequency SSH traffic created in the lab |
| Capture Completion | Packet capture stopped after activity was generated | `74,630` packets captured; `0` packets dropped by kernel |
| Zeek Processing | PCAP processed to generate protocol logs | `conn.log`, `ssh.log` and supporting logs retained |
| Connection Analysis | Port `22` and SSH-source frequency reviewed | `192.168.206.128` identified as dominant source with `2,225` connections |
| Automated Detection | Python detector executed | Possible SSH brute force alert generated |

## Attack Simulation Evidence

The controlled attack activity was generated from Kali Linux using Hydra against the Windows SSH service. The retained screenshot shows the following command pattern:

```bash
hydra -l testuser -P /usr/share/wordlists/rockyou.txt ssh://192.168.206.133 -t 4 -V
```

This command tested passwords from the supplied wordlist against the account name `testuser` on the SSH service of the target host. The screenshot documents repeated visible attempts including common password candidates such as `123456`, `password`, and `rockyou`.

Evidence:

- [`hydra_bruteforce_attack.png`](../screenshots/ssh-bruteforce/hydra_bruteforce_attack.png)

## Initial Validation

### Network Reachability

Connectivity between the Kali source system and the Windows target was confirmed before attack generation.

| Source | Target | Result |
|---|---|---|
| Kali Linux | `192.168.206.133` | ICMP replies received successfully |

Evidence:

- [`kali_to_windows_ping.png`](../screenshots/ssh-bruteforce/kali_to_windows_ping.png)

### SSH Service Exposure

Nmap verification confirmed the attack surface required for the scenario:

| Port | State | Service |
|---:|---|---|
| `22/tcp` | Open | `ssh` |

Evidence:

- [`nmap_ssh_port_open.png`](../screenshots/ssh-bruteforce/nmap_ssh_port_open.png)

## Traffic Collection

The Ubuntu monitoring host captured traffic using `tcpdump` on the monitored interface and saved the output as `ssh_bruteforce.pcap`. The retained capture summary shows:

| Capture Metric | Observed Value |
|---|---:|
| Packets Captured | `74,630` |
| Packets Received by Filter | `74,636` |
| Packets Dropped by Kernel | `0` |

The absence of dropped packets supports the completeness of the packet evidence for this lab activity.

Evidence:

- [`tcpdump_capture_started.png`](../screenshots/ssh-bruteforce/tcpdump_capture_started.png)
- [`tcpdump_capture_stopped.png`](../screenshots/ssh-bruteforce/tcpdump_capture_stopped.png)

## Zeek Log Analysis

After packet collection, the PCAP was processed with Zeek. The generated evidence included `conn.log`, `ssh.log`, `dns.log`, `dhcp.log`, `packet_filter.log`, `reporter.log`, and `weird.log`.

A source-frequency review of SSH traffic identified the following pattern:

| Finding | Result |
|---|---:|
| Suspected Source IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Destination Port | `22/tcp` |
| Connections Identified for Source-to-Target Pair | `2,225` |
| Connections Classified as `ssh` Service | `2,223` |
| Connections Without SSH Service Classification | `2` |

The concentration of SSH connections from one source to one target indicates automated activity rather than a small number of normal interactive authentication attempts.

Evidence:

- [`zeek_logs_generated.png`](../screenshots/ssh-bruteforce/zeek_logs_generated.png)
- [`conn_log_analysis.png`](../screenshots/ssh-bruteforce/conn_log_analysis.png)
- [`attacker_ip_identification.png`](../screenshots/ssh-bruteforce/attacker_ip_identification.png)

## Packet-Level Validation

Wireshark review was performed on the preserved PCAP file. Applying a filter for TCP port `22` displayed the SSH-related traffic, while narrowing the filter to source IP `192.168.206.128` isolated the activity from the suspected source.

| Validation View | Observation |
|---|---|
| `tcp.port == 22` | Large volume of SSH-related traffic associated with the target port |
| `ip.src == 192.168.206.128 && tcp.port == 22` | Repeated source-originated traffic directed to SSH on the Windows target |
| Protocol display | SSHv2 exchanges and repeated connection behaviour visible in the capture |

The Wireshark evidence corroborates the Zeek-based identification of the source and targeted service.

Evidence:

- [`wireshark_ssh_filter.png`](../screenshots/ssh-bruteforce/wireshark_ssh_filter.png)
- [`wireshark_tcp_stream.png`](../screenshots/ssh-bruteforce/wireshark_tcp_stream.png)

## Automated Detection Result

A Python detector was executed against the retained connection evidence to identify unusually high SSH connection activity. The alert output recorded:

```text
[ALERT] Possible SSH brute force: 192.168.206.128 -> 192.168.206.133 | Connections: 2225
```

| Alert Attribute | Result |
|---|---|
| Detection Type | Possible SSH Brute Force |
| Suspected Source IP | `192.168.206.128` |
| Target IP | `192.168.206.133` |
| Alerted Connection Count | `2,225` |

The detector output aligns with the connection-count evidence observed during Zeek analysis.

Evidence:

- [`python_detection_alert.png`](../screenshots/ssh-bruteforce/python_detection_alert.png)
- [`detect_ssh_bruteforce.py`](../detection-scripts/detect_ssh_bruteforce.py)

## Indicators of Activity

| Indicator | Value |
|---|---|
| Suspicious Source IP | `192.168.206.128` |
| Target Host IP | `192.168.206.133` |
| Target Port | `22/tcp` |
| Target Service | SSH |
| Username Used in Controlled Simulation | `testuser` |
| Activity Generator | Hydra password-guessing tool |
| Alerted Connection Count | `2,225` |
| Packet Capture Volume | `74,630` captured packets |

## MITRE ATT&CK Mapping

| Tactic | Technique | ID | Justification |
|---|---|---|---|
| Credential Access | Brute Force | `T1110` | Repeated automated password guesses were directed at an exposed SSH authentication service. |

## Severity and Impact Assessment

This event is classified as **High severity for detection and investigation purposes** because:

- SSH was confirmed open on the target host.
- Automated password attempts were generated against a named account.
- A single source produced `2,225` observed SSH-related connections toward one target.
- The activity represents a direct attempt to gain authenticated access.

The evidence confirms brute force activity in the lab; it does not confirm that any password attempt succeeded. No claim of unauthorized access, successful login, or post-authentication action is made in this report.

## Recommended Response Actions

| Priority | Recommendation | Purpose |
|---:|---|---|
| 1 | Investigate the source host generating repeated SSH attempts | Determine whether activity is authorised or malicious |
| 2 | Review SSH authentication logs on the target | Confirm failed versus successful login outcomes |
| 3 | Enforce account lockout, rate limiting or fail2ban-equivalent controls | Reduce effectiveness of repeated password attempts |
| 4 | Disable password-based SSH authentication where feasible | Reduce credential-guessing attack surface |
| 5 | Restrict SSH access to approved administration networks | Limit exposure of remote access services |
| 6 | Preserve PCAP, Zeek telemetry and detector evidence | Support investigation and timeline reconstruction |

## Evidence Screenshot Index

| Screenshot | Evidence Demonstrated |
|---|---|
| [`kali_to_windows_ping.png`](../screenshots/ssh-bruteforce/kali_to_windows_ping.png) | Source-to-target connectivity validation |
| [`nmap_ssh_port_open.png`](../screenshots/ssh-bruteforce/nmap_ssh_port_open.png) | Open SSH service on the Windows target |
| [`tcpdump_capture_started.png`](../screenshots/ssh-bruteforce/tcpdump_capture_started.png) | Packet capture initiated before activity |
| [`hydra_bruteforce_attack.png`](../screenshots/ssh-bruteforce/hydra_bruteforce_attack.png) | Controlled password-guessing generation |
| [`tcpdump_capture_stopped.png`](../screenshots/ssh-bruteforce/tcpdump_capture_stopped.png) | Capture completion and packet totals |
| [`zeek_logs_generated.png`](../screenshots/ssh-bruteforce/zeek_logs_generated.png) | Zeek logs generated from PCAP |
| [`conn_log_analysis.png`](../screenshots/ssh-bruteforce/conn_log_analysis.png) | SSH connection analysis |
| [`attacker_ip_identification.png`](../screenshots/ssh-bruteforce/attacker_ip_identification.png) | Suspicious source identification |
| [`wireshark_ssh_filter.png`](../screenshots/ssh-bruteforce/wireshark_ssh_filter.png) | Packet review focused on port `22` |
| [`wireshark_tcp_stream.png`](../screenshots/ssh-bruteforce/wireshark_tcp_stream.png) | Source-filtered SSH traffic evidence |
| [`python_detection_alert.png`](../screenshots/ssh-bruteforce/python_detection_alert.png) | Python detector alert |

## Analyst Conclusion

The investigation confirmed automated SSH brute force activity from `192.168.206.128` against the Windows SSH service at `192.168.206.133:22`. Service verification established that SSH was open on the target. The controlled Hydra activity generated repeated authentication attempts, while Zeek analysis identified `2,225` source-to-target connections associated with the SSH attack path. Wireshark validation and the Python detector alert supported the same finding.

The incident is mapped to `T1110 - Brute Force`. The available evidence confirms repeated password-guessing activity but does not confirm successful authentication or compromise. This case demonstrates a complete network-focused investigation workflow: attack-surface validation, packet capture, Zeek log review, source identification, packet-level validation, automated alerting, and incident reporting.
