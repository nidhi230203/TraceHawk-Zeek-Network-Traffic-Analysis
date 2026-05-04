\# ⚙️ Lab Setup \& Methodology



\## 1. Introduction



This project was developed in a controlled virtual lab environment to simulate and detect network-based attacks using Zeek. The objective is to replicate a real-world Security Operations Center (SOC) workflow, focusing on traffic capture, analysis, detection, and reporting.



\---



\## 2. Lab Architecture



The lab consists of three virtual machines connected via an isolated Host-Only network:



| Machine        | Role               | Operating System |

|---------------|--------------------|------------------|

| Kali Linux    | Attacker           | Kali Linux       |

| Windows 11    | Target System      | Windows 11       |

| Ubuntu        | Monitoring System  | Ubuntu Linux     |



\### Network Configuration

\- Network Type: Host-Only

\- All machines are connected to the same virtual network

\- Systems reside within the same subnet



\---



\## 3. Tools \& Technologies



| Tool        | Purpose |

|------------|--------|

| Zeek       | Network traffic analysis and logging |

| tcpdump    | Packet capture |

| Wireshark  | Packet-level inspection |

| Hydra      | SSH brute force attack simulation |

| Nmap       | Port and service discovery |



\---



\## 4. IP Addressing Scheme



Each machine was assigned a unique IP address within the same subnet:



Kali Linux   → 192.168.206.128  

Windows 11   → 192.168.206.133  

Ubuntu       → 192.168.206.xxx  



All machines were verified for connectivity using ping.



\---



\## 5. Target Configuration (Windows 11)



To simulate an attackable service, SSH was enabled on the Windows machine.



Steps performed:



1\. Installed OpenSSH Server  

2\. Started SSH service:

&#x20;  Start-Service sshd  

3\. Set service to start automatically:

&#x20;  Set-Service -Name sshd -StartupType Automatic  

4\. Allowed SSH traffic through firewall:

&#x20;  New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22  



\---



\## 6. Attack Simulation (Kali Linux)



A brute force attack was performed using Hydra targeting the SSH service.



Step 1: Verify SSH Port

nmap -p 22 192.168.206.133



Step 2: Launch Attack

hydra -l testuser -P /usr/share/wordlists/rockyou.txt ssh://192.168.206.133 -t 4 -V



\- Multiple login attempts were generated  

\- Traffic targeted port 22 (SSH)  

\- Attack duration was approximately 3–5 minutes  



\---



\## 7. Packet Capture (Ubuntu)



Network traffic was captured during the attack using tcpdump.



Command used:

sudo tcpdump -i ens34 -nn -w ssh\_bruteforce.pcap



Key points:

\- Capture started before the attack  

\- Capture stopped manually after the attack  

\- Output stored as a PCAP file for analysis  



\---



\## 8. Zeek Log Generation



Captured traffic was processed using Zeek.



Command used:

zeek -r ssh\_bruteforce.pcap



Generated logs include:

\- conn.log (connection-level data)  

\- ssh.log (authentication attempts)  

\- dns.log (DNS queries)  

\- dhcp.log, weird.log, and other supporting logs  



\---



\## 9. Traffic Analysis Approach



\### Zeek-Based Analysis

\- Filtered SSH traffic using port 22  

\- Identified repeated connections  

\- Detected abnormal connection patterns  

\- Extracted attacker IP using frequency analysis  



\### Wireshark Analysis

\- Applied filter:

&#x20; tcp.port == 22  

\- Inspected TCP handshake behavior  

\- Observed repeated connection attempts  

\- Verified attack pattern at packet level  



\---



\## 10. Detection Methodology



The attack was identified using behavior-based detection techniques:



\- High volume of SSH connections from a single source IP  

\- Repeated short-duration sessions  

\- Failed connection states  

\- Consistent targeting of a single destination  



This approach enables detection without prior knowledge of the attacker.



\---



\## 11. Workflow Summary



Attack Simulation → Packet Capture → Zeek Log Generation → Analysis → Detection → Reporting



\---



\## 12. Challenges Faced



\- Initial network misconfiguration between virtual machines  

\- Incorrect interface selection during packet capture  

\- Missing SSH logs due to incomplete attack execution  

\- Service configuration issues on the Windows system  



\---



\## 13. Key Learnings



\- Proper network configuration is critical for accurate analysis  

\- Packet capture must be validated before analysis  

\- Zeek provides structured visibility into large traffic datasets  

\- Behavior-based detection is effective for unknown threats  

\- Combining log analysis with packet inspection improves accuracy  



\---



\## 14. Conclusion



This lab demonstrates a practical SOC workflow for detecting brute force attacks using network traffic analysis. The project highlights real-world techniques for identifying malicious activity through logs and packet-level investigation, without relying on prior assumptions.



