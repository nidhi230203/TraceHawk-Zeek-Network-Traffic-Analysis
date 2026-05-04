\# 🔍 Brute Force Attack Analysis



\## 1. Overview



This analysis focuses on detecting and investigating an SSH brute force attack using Zeek logs and packet capture data. The goal is to identify suspicious behavior, determine the attacker, and understand the attack pattern.



\---



\## 2. Data Sources



The following data sources were used:



\- PCAP file captured using tcpdump

\- Zeek logs:

&#x20; - conn.log

&#x20; - ssh.log

&#x20; - dns.log

&#x20; - dhcp.log

&#x20; - weird.log



\---



\## 3. Initial Observation



After processing the captured traffic using Zeek, multiple connection attempts were observed targeting port 22 (SSH). This indicated potential brute force activity.



\---



\## 4. Filtering SSH Traffic



SSH traffic was isolated using:



Command:

cat conn.log | zeek-cut id.orig\_h id.resp\_h id.resp\_p service | grep 22



This helped identify all connections made to the SSH service.



\---



\## 5. Identifying Suspicious Behavior



The following anomalies were observed:



\- High number of connections from a single source IP

\- Repeated attempts to the same destination IP

\- Short-lived connections

\- Continuous traffic pattern



\---



\## 6. Attacker Identification



The attacker was identified using frequency analysis:



Command:

cat conn.log | zeek-cut id.orig\_h id.resp\_p | grep 22 | sort | uniq -c | sort -nr



Result:

The IP address with the highest number of SSH connection attempts was identified as the attacker.



\---



\## 7. Traffic Pattern Analysis



Key characteristics of the attack:



\- Repeated connection attempts to port 22

\- Same source IP targeting the same destination

\- Rapid sequence of connection attempts

\- No successful session establishment



\---



\## 8. Packet-Level Verification (Wireshark)



Wireshark was used to validate findings:



Filter used:

tcp.port == 22



Observations:



\- Multiple TCP SYN packets

\- Repeated connection attempts

\- Incomplete TCP handshakes

\- Pattern consistent with brute force attack



\---



\## 9. Detection Logic



The attack was detected based on:



\- Frequency of connection attempts

\- Repetition of source IP

\- Consistent targeting behavior

\- Abnormal traffic volume



This indicates automated brute force activity.



\---



\## 10. Key Findings



\- A single IP generated the majority of SSH traffic

\- Target system received repeated login attempts

\- Traffic pattern matched brute force behavior

\- Attack was detected without prior knowledge of attacker



\---



\## 11. Conclusion



The analysis successfully identified a brute force attack using network traffic analysis techniques. By examining Zeek logs and packet-level data, the attacker was detected based on behavioral patterns rather than assumptions.



This demonstrates practical SOC-level analysis and threat detection capabilities.



