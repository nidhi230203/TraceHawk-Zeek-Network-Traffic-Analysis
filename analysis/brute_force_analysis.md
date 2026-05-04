# Brute Force Attack Analysis

## Overview

This document presents the analysis of an SSH brute force attack captured in the TraceHawk network forensics lab. The objective of this analysis is to identify suspicious SSH activity, determine the attacking source, validate the behavior using Zeek logs and Wireshark, and document the findings in a SOC-style format.

The investigation followed this workflow: Attack Traffic Collection -> Zeek Log Analysis -> Attacker Identification -> Packet Validation -> Detection Conclusion.

## Data Sources Used

The following artifacts were used during the investigation:

| Data Source | File / Tool | Purpose |
|---|---|---|
| Packet Capture | ssh_bruteforce.pcap | Raw network evidence |
| Zeek Connection Log | conn.log | Connection-level traffic analysis |
| Zeek SSH Log | ssh.log | SSH session visibility |
| Zeek DNS Log | dns.log | DNS traffic review |
| Wireshark | PCAP analysis | Packet-level validation |
| Python Script | detect_ssh_bruteforce.py | Automated detection logic |

## Investigation Scope

The analysis focuses on traffic related to SSH brute force activity against the Windows 11 target system.

| Field | Value |
|---|---|
| Attack Type | SSH Brute Force |
| Target Service | SSH |
| Target Port | TCP/22 |
| Attacker Machine | Kali Linux |
| Target Machine | Windows 11 |
| Monitoring System | Ubuntu with Zeek, tcpdump, and Wireshark |

## Initial Observation

After processing the captured PCAP file with Zeek, multiple logs were generated. The main log used for identifying the brute force pattern was conn.log, because it provides connection-level details such as source IP, destination IP, destination port, protocol, service, duration, and connection state.

The investigation started by filtering connections related to SSH traffic.

Command used:

cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto service duration conn_state | grep 22

This command isolates traffic where the destination port is TCP/22.

## SSH Traffic Filtering

SSH-related traffic was filtered from conn.log using the destination port.

Command used:

cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p service | grep 22

This output shows repeated SSH connection attempts from a source IP toward the target system.

The important fields in this command are:

| Field | Meaning |
|---|---|
| id.orig_h | Source IP address |
| id.resp_h | Destination IP address |
| id.resp_p | Destination port |
| service | Detected service |

## Attacker Identification

The attacker was identified using frequency-based analysis. Instead of assuming the Kali Linux machine was the attacker, the logs were used to determine which source IP generated the highest number of SSH connection attempts.

Command used:

cat conn.log | zeek-cut id.orig_h id.resp_p | grep 22 | sort | uniq -c | sort -nr

This command counts how many times each source IP connected to port 22. A source IP generating an unusually high number of SSH connections is considered suspicious because normal users typically do not create a large number of repeated SSH attempts in a short time window.

## Suspicious Behavior Observed

The following behavior was observed during the analysis:

- Repeated SSH connection attempts toward the same target system
- High concentration of traffic from a single source IP
- Consistent targeting of TCP port 22
- Short-duration connections
- Pattern consistent with automated password guessing

These indicators strongly suggest brute force activity.

## Zeek Log Interpretation

Zeek conn.log provides useful evidence for identifying suspicious traffic patterns.

| Field | Analysis Value |
|---|---|
| id.orig_h | Helps identify the source system |
| id.resp_h | Helps identify the target system |
| id.resp_p | Confirms the targeted service port |
| service | Helps confirm SSH-related traffic |
| duration | Helps identify short repeated sessions |
| conn_state | Helps understand connection behavior |

For brute force detection, the most important indicator was repeated SSH traffic from one source IP to the target system.

## Wireshark Validation

Wireshark was used to validate the findings at the packet level.

Display filter used:

tcp.port == 22

After identifying the suspicious source IP from Zeek logs, a more focused filter can be applied:

ip.src == suspected-attacker-ip && tcp.port == 22

Wireshark helped confirm repeated SSH traffic, the same source communicating with the same target, multiple TCP connection attempts, and traffic behavior consistent with brute force activity.

## Detection Logic

The detection logic is based on behavior rather than prior knowledge of the attacker. A source IP is considered suspicious when it generates repeated SSH connections, targets the same destination repeatedly, communicates on TCP port 22, and creates a high connection count in a short time period.

This logic can be automated using Python to alert on high-frequency SSH attempts.

## Python-Based Detection

The Python detection script checks Zeek conn.log and counts SSH connection attempts per source-destination pair.

Detection rule:

If one source IP generates SSH connection attempts above a defined threshold, flag it as a possible brute force attack.

This adds a basic detection engineering component to the project.

## Findings Summary

| Finding | Observation |
|---|---|
| Targeted Service | SSH |
| Target Port | TCP/22 |
| Attack Pattern | Repeated SSH attempts |
| Detection Source | Zeek conn.log |
| Validation Source | Wireshark PCAP analysis |
| Detection Type | Behavior-based |
| Attack Category | Brute Force |

## MITRE ATT&CK Mapping

| Tactic | Technique | ID |
|---|---|---|
| Credential Access | Brute Force | T1110 |

This attack maps to MITRE ATT&CK technique T1110 because the attacker attempted repeated authentication attempts against the SSH service.

## Impact Assessment

If this attack succeeded in a real environment, the attacker could gain unauthorized access to the target system. Successful SSH compromise may allow command execution, persistence, lateral movement, or further internal reconnaissance. In this lab, the attack was simulated in a controlled environment for detection and analysis purposes.

## Recommended Mitigations

Recommended defensive actions include:

- Disable SSH if it is not required
- Enforce strong password policies
- Implement account lockout after repeated failed attempts
- Restrict SSH access to trusted IP addresses
- Use key-based authentication instead of password authentication
- Enable multi-factor authentication where possible
- Monitor repeated failed login attempts
- Alert on high-frequency SSH connections from a single source

## Analyst Conclusion

The investigation successfully identified SSH brute force behavior using network traffic analysis. Zeek logs were used to detect repeated SSH connection attempts and identify the suspicious source IP without relying on prior assumptions. Wireshark was used to validate the packet-level behavior, and Python-based detection logic was added to automate the identification of similar activity.

This analysis demonstrates practical SOC skills including network traffic analysis, log investigation, attacker identification, packet validation, detection logic, and incident documentation.
