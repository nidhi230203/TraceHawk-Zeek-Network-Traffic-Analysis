# Lab Setup and Methodology

## Introduction

This document describes the setup and methodology used for the TraceHawk Network Forensics and Threat Detection Lab. The lab was created to simulate a real-world SOC workflow for detecting SSH brute force activity using network traffic analysis. The project focuses on practical execution, evidence collection, log generation, analysis, detection, and reporting.

## Lab Environment

The lab consists of three virtual machines connected through an isolated Host-Only network.

| Machine | Role | Operating System | Purpose |
|---|---|---|---|
| Kali Linux | Attacker | Kali Linux | Used to perform reconnaissance and SSH brute force attack |
| Windows 11 | Target System | Windows 11 | Hosted the SSH service targeted during the attack |
| Ubuntu | Monitoring Node | Ubuntu Linux | Used for packet capture, Zeek log generation, and traffic analysis |

## Network Configuration

All systems were connected to the same Host-Only network to keep the attack traffic isolated from the external network. This ensured that the activity remained controlled and safe for lab testing.

Example IP addressing used in the lab:

| System | Example IP Address |
|---|---|
| Kali Linux | 192.168.206.128 |
| Windows 11 | 192.168.206.133 |
| Ubuntu Monitoring Node | 192.168.206.xxx |

Connectivity was verified between systems before starting the attack simulation. This step ensured that Kali Linux could reach the Windows target and that the Ubuntu monitoring system could observe network traffic on the correct interface.

## Tools Used

| Tool | System | Purpose |
|---|---|---|
| Nmap | Kali Linux | Service discovery and port verification |
| Hydra | Kali Linux | SSH brute force simulation |
| tcpdump | Ubuntu | Packet capture |
| Zeek | Ubuntu | Network log generation and traffic analysis |
| Wireshark | Ubuntu or Windows | Packet-level validation |
| Python | Ubuntu or Windows | Detection logic implementation |

## Target System Configuration

The Windows 11 system was configured as the target machine. OpenSSH Server was enabled to expose SSH on TCP port 22. This allowed the lab to simulate a realistic SSH brute force attack scenario.

The target service was verified from Kali Linux using Nmap.

Command used:

nmap -p 22 192.168.206.133

Expected result:

22/tcp open ssh

This confirmed that the SSH service was reachable before starting the brute force simulation.

## Monitoring Interface Identification

Before capturing traffic, the correct network interface on Ubuntu was identified. This step is important because selecting the wrong interface can result in empty or incomplete packet captures.

Command used:

ip a

The correct interface was selected based on the Host-Only network IP range. In this lab, the monitoring interface used for capture was ens34.

## Packet Capture Methodology

Packet capture was performed on the Ubuntu monitoring node using tcpdump. The capture was started before launching the attack to ensure the full attack window was recorded.

Command used:

sudo tcpdump -i ens34 -nn -w ssh_bruteforce.pcap

Explanation:

- ens34 was the monitoring interface connected to the Host-Only network
- -nn disabled hostname and port name resolution for cleaner output
- -w saved the captured packets into a PCAP file
- ssh_bruteforce.pcap was used as the raw evidence file

The capture was manually stopped after the attack completed.

## Attack Simulation

The SSH brute force attack was launched from Kali Linux using Hydra. The attack targeted the Windows 11 machine on TCP port 22.

Command used:

hydra -l testuser -P /usr/share/wordlists/rockyou.txt ssh://192.168.206.133 -t 4 -V

Explanation:

- -l specifies the username
- -P specifies the password wordlist
- ssh://192.168.206.133 specifies the SSH target
- -t 4 limits parallel tasks
- -V prints each attempt for visibility

The attack was executed for a limited time in a controlled lab environment.

## Zeek Log Generation

After the packet capture was completed, the PCAP file was processed using Zeek to generate structured logs.

Command used:

zeek -r ssh_bruteforce.pcap

This generated multiple Zeek logs that were used for analysis.

Important logs generated:

| Log File | Purpose |
|---|---|
| conn.log | Connection-level traffic visibility |
| ssh.log | SSH session visibility |
| dns.log | DNS query activity |
| dhcp.log | DHCP activity |
| weird.log | Protocol anomalies |
| packet_filter.log | Packet filter information |
| reporter.log | Zeek runtime messages |

## Analysis Workflow

The analysis followed a SOC-style investigation workflow.

Workflow used:

Attack Simulation -> Packet Capture -> Zeek Log Generation -> Traffic Analysis -> Detection -> Reporting

The main analysis focused on identifying repeated SSH connection attempts toward port 22 and determining which source IP generated the suspicious activity.

## SSH Traffic Filtering

SSH traffic was filtered from Zeek conn.log using the destination port.

Command used:

cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p service | grep 22

This helped isolate traffic related to the SSH service.

## Attacker Identification Method

The suspected attacker was identified using frequency-based analysis instead of assuming the Kali Linux IP manually.

Command used:

cat conn.log | zeek-cut id.orig_h id.resp_p | grep 22 | sort | uniq -c | sort -nr

This command counted SSH connection attempts per source IP. The source IP with the highest number of SSH attempts was treated as the suspicious source.

## Wireshark Validation

Wireshark was used to validate the Zeek findings at the packet level.

Display filter used:

tcp.port == 22

After identifying the suspicious source IP, focused analysis can be done using:

ip.src == suspected-attacker-ip && tcp.port == 22

Wireshark helped confirm repeated SSH connection attempts and supported the detection conclusion.

## Detection Logic

The brute force behavior was detected based on repeated SSH connections from a single source to the same target on TCP port 22. The detection approach was behavior-based and did not rely on prior knowledge of the attacker.

Detection indicators included:

- Repeated SSH connection attempts
- Same source IP targeting the same destination
- High connection frequency
- Short-duration sessions
- Traffic directed toward TCP port 22

## Python Detection Script

A Python script was included to automate basic brute force detection using Zeek conn.log. The script counts SSH connection attempts and raises an alert when attempts exceed a defined threshold.

The script is stored in:

detection-scripts/detect_ssh_bruteforce.py

## Evidence Collected

The following evidence was collected and organized in the project repository:

| Evidence Type | Location |
|---|---|
| PCAP file | pcaps/ssh_bruteforce.pcap |
| Zeek logs | zeek-logs/ssh-bruteforce/ |
| Detection script | detection-scripts/detect_ssh_bruteforce.py |
| Screenshots | screenshots/ssh-bruteforce/ |
| Analysis report | analysis/brute_force_analysis.md |
| Incident report | incident-reports/ssh_bruteforce_report.md |

## Challenges Faced

During the setup and execution, several practical issues were encountered and resolved:

- Incorrect interface selection during packet capture
- Zeek command not available in PATH initially
- Incomplete PCAP capture during early attempts
- SSH service connectivity issues
- Need to identify the attacker from logs rather than lab assumptions

These challenges helped improve the reliability of the final workflow.

## Key Learnings

This setup provided practical experience in:

- Building an isolated network traffic analysis lab
- Capturing packets using tcpdump
- Generating structured logs using Zeek
- Filtering and analyzing SSH traffic
- Identifying attacker IP through log evidence
- Validating findings using Wireshark
- Writing SOC-style documentation and reports

## Conclusion

The TraceHawk lab setup successfully demonstrates a practical SOC workflow for detecting SSH brute force activity using Zeek and packet analysis. The environment was designed to safely simulate attack traffic, capture evidence, generate logs, identify suspicious behavior, and document findings in a professional format.
