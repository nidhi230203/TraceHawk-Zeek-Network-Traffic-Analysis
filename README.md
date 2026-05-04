\# 🦅 TraceHawk: Network Forensics \& Threat Detection Lab



\## 📌 Overview



TraceHawk is a SOC-style cybersecurity project focused on detecting network-based attacks using Zeek. The project simulates a real-world SSH brute force attack in a controlled lab environment and demonstrates how attackers can be identified through traffic analysis.



This project follows a practical workflow used in Security Operations Centers:



Attack → Capture → Analyze → Detect → Investigate → Report



\---



\## 🎯 Objectives



\- Capture network traffic using tcpdump

\- Analyze logs using Zeek (conn.log, ssh.log)

\- Detect SSH brute force attacks

\- Identify attacker IP without prior knowledge

\- Perform packet analysis using Wireshark

\- Implement detection logic using Python



\---



\## 🏗 Lab Architecture



\- Attacker: Kali Linux

\- Target: Windows 11 (SSH enabled)

\- Monitoring: Ubuntu (Zeek, tcpdump, Wireshark)

\- Network: Host-Only isolated environment





!\[Architecture](architecture/network\_architecture.png)



\---



\## ⚔️ Attack Scenario



An SSH brute force attack was simulated using Hydra from Kali Linux targeting the Windows system.



Command used:



hydra -l testuser -P /usr/share/wordlists/rockyou.txt ssh://192.168.206.133 -t 4 -V



\---



\## 📡 Data Collection



Network traffic was captured using tcpdump:



sudo tcpdump -i ens34 -nn -w ssh\_bruteforce.pcap



The captured PCAP file was analyzed using Zeek:



zeek -r ssh\_bruteforce.pcap



\---



\## 🔍 Detection Methodology



The attack was detected using Zeek logs by:



\- Filtering SSH traffic (port 22)

\- Identifying repeated connections

\- Detecting abnormal traffic patterns

\- Performing frequency-based analysis



Example detection command:



cat conn.log | zeek-cut id.orig\_h id.resp\_p | grep 22 | sort | uniq -c | sort -nr



\---

\## 📸 Attack Execution \& Analysis Screenshots



\### 🔹 Network Connectivity Verification

!\[Ping Test](screenshots/ssh-bruteforce/kali\_to\_windows\_ping.png)



\---



\### 🔹 SSH Service Discovery (Nmap Scan)

!\[Nmap Scan](screenshots/ssh-bruteforce/nmap\_ssh\_port\_open.png)



\---



\### 🔹 Packet Capture Started (tcpdump)

!\[tcpdump Start](screenshots/ssh-bruteforce/tcpdump\_capture\_started.png)



\---



\### 🔹 SSH Brute Force Attack (Hydra)

!\[Hydra Attack](screenshots/ssh-bruteforce/hydra\_bruteforce\_attack.png)



\---



\### 🔹 Packet Capture Stopped

!\[tcpdump Stop](screenshots/ssh-bruteforce/tcpdump\_capture\_stopped.png)



\---



\### 🔹 Zeek Logs Generated

!\[Zeek Logs](screenshots/ssh-bruteforce/zeek\_logs\_generated.png)



\---



\### 🔹 Attacker Identification (Zeek Analysis)

!\[Attacker IP](screenshots/ssh-bruteforce/attacker\_ip\_identification.png)



\---



\### 🔹 Connection Log Analysis

!\[conn.log](screenshots/ssh-bruteforce/conn\_log\_analysis.png)



\---



\### 🔹 Wireshark Analysis (SSH Traffic)

!\[Wireshark Filter](screenshots/ssh-bruteforce/wireshark\_ssh\_filter.png)



\---



\### 🔹 TCP Stream / Attack Pattern

!\[TCP Stream](screenshots/ssh-bruteforce/wireshark\_tcp\_stream.png)



\---



\### 🔹 Python Detection Output

!\[Detection Script](screenshots/ssh-bruteforce/python\_detection\_alert.png)





\## 🚨 Key Findings



\- High volume of SSH attempts from a single IP

\- Repeated short-duration connections

\- Consistent targeting of the same system

\- Behavior indicates automated brute force attack



\---



\## 🧠 Skills Demonstrated



\- Network Traffic Analysis (NTA)

\- Zeek Log Analysis

\- Wireshark Packet Inspection

\- Attack Detection \& Investigation

\- SOC Workflow Implementation

\- Python-based Detection Logic



\---



\## 📂 Project Structure



TraceHawk/

│

├── setup/

├── analysis/

├── attacks/

├── incident-reports/

├── pcaps/

├── zeek-logs/

├── detection-scripts/

├── screenshots/

└── architecture/



\---



\## 📌 Conclusion



This project demonstrates how network-level monitoring can be used to detect brute force attacks without relying on endpoint logs. It highlights practical SOC analyst skills including traffic analysis, attacker identification, and incident investigation.



\---



\## ⚠️ Disclaimer



This project is created for educational purposes only. All activities were performed in a controlled lab environment.



