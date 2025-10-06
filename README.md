# Creacode SIP Application Server (IVR Platform)

## Table of Contents
- [Features](#features)
- [Use Cases](#use-cases)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Deployment Steps](#deployment-steps)
  - [Voice File Generation](#voice-file-generation)
- [Deployment Example](#deployment-example)
- [Test Call Flow](#test-call-flow)
  - [Main.txt – Entry Point](#maintxt-entry-point)
  - [NewSession.txt – Session Logic and Interaction](#newsessiontxt-session-logic-and-interaction)
  - [Ringing.txt – Bridging to Live Agent](#ringingtxt-bridging-to-live-agent)
  - [CallMonitor.txt – Call Supervision and Media Handling](#callmonitortxt-call-supervision-and-media-handling)
- [Outbound Routing Configuration](#outbound-routing-configuration)

# Features

### Carrier-Grade SIP and Voice Processing Server
Designed for high-performance, scalable SIP call handling and advanced voice processing.

### Proven in Production
Over 10 years of proven runtime reliability in production environments.

### Real-Time Event-Driven Script Engine
Enables rapid service development with hot-reloadable call flows. Supported capabilities include:

- SIP call control and multi-language RTP voice processing via scripts  
- On-the-fly compilation and runtime script reloading  
- DTMF detection and processing  
- Outbound Web Service API calls  
- Direct SQL database queries  
- RADIUS AAA integration  
- String manipulation and basic math operations  
- Timers and user-defined scripting functions  
- Voice recording with email delivery  
- Outbound email (text messages)

### Additional Core Features
- Number prefix-based routing  
- IP ACL filtering for enhanced security  
- Integrated SIP Registrar  
- T.38 fax support  
- Runtime configuration via Telnet CLI  
- Modular logging (script, app, SIP, RTP) for debugging and traceability  
- Database-driven CDR (Call Detail Record) generation  

---

## Use Cases

The IVR platform simplifies development and deployment of a wide range of telephony applications, including:

- Inbound voice interaction/response services for call centers and enterprise PBXs  
- Outbound dialing campaigns (e.g., surveys, customer feedback collection)  
- Predictive dialing scenarios  
- Data-driven call flow applications without voice playback  
- Voice recording and archival services  
- **Prepaid and account-based services**, such as:  
  - Querying prepaid balances, usage limits, or billing status  
  - Real-time account management through RADIUS AAA  
  - Credit card information services (e.g., balance inquiry, credit/debt checks) via direct database lookup or Web API call — demonstrated in the `Scripts\cc_info_service` sample application  

---

## Deployment

### Prerequisites
The IVR platform is deployed on **Windows** using an automated PowerShell script.  
The following components are required:

- Windows Server environment with administrative privileges  
- Microsoft Visual C++ Redistributable (installed automatically by script)  
- Telnet Client (enabled by script for runtime CLI access)  
- PostgreSQL 17.6 database server  
- psqlODBC driver (for ODBC access)  
- Python 3.13.7 (downloaded and installed if not present)  
- Python libraries: `gTTS`, `pydub`  
- FFmpeg 8.0 (used by `pydub` for audio processing)  

### Deployment Steps

Deployment is fully automated via the `deploy-ivr.ps1` script.  
It supports both **all-in-one execution** and **step-by-step execution** for granular control.

#### Usage
```powershell
.\deploy-ivr.ps1 -all        # Run all 12 steps
.\deploy-ivr.ps1 -Step N     # Run a specific step (1..12)
.\deploy-ivr.ps1 -help       # Show help message
```

#### Steps performed by the script
1. Install Microsoft VC++ Redistributable  
2. Enable Telnet Client  
3. Create folder structure (`C:\CreacodeSAS`)  
4. Copy application binaries  
5. Copy resource directories (scripts, configs, voice assets)  
6. Install PostgreSQL (downloaded if not available)  
7. Install ODBC driver  
8. Create ODBC DSN (`creacodesas_pg_local`)  
9. Restore database from `creacodesas_postgres_backup.sql`  
10. Install voice generation prerequisites (Python, gTTS, pydub, ffmpeg)  
11. Generate multilingual voice files using `generate_all_voice.py`  
12. Finalize and start the IVR service:  
    - Patch `.ini` files  
    - Compile service scripts  
    - Install/start Windows service  
    - Apply firewall rules  

---

### Voice File Generation

- Voice prompts are created under `Voice/GenerateVoiceFiles/`.  
- Each generation script builds localized voice folders (e.g., `english`, `turkish`, `german`).  
- During generation, language folders are merged into a central `CreacodeSAS/` staging directory. Existing files are preserved to avoid overwriting.  
- Once generation is complete, the entire `CreacodeSAS/` folder is moved into the `Voice/` directory at the deployment root, alongside other system folders (`Bin`, `Scripts`, `LOG`, etc.).  
- The original temporary folders in subdirectories are cleaned up after merging.  

---

## Deployment Example

### 1. Clone or Copy Deployment Package
Obtain the deployment package from the GitHub repository and extract it into a working directory (e.g., `C:\IVR\Deployment`).  

This directory contains:

- `deploy-ivr.ps1` (main deployment script)  
- Binaries (`Bin/`), scripts (`Scripts/`), and configuration files  
- PostgreSQL backup file (`creacodesas_postgres_backup.sql`)  
- Voice generation scripts under `Voice/GenerateVoiceFiles/`  

### 2. Run Full Deployment
Open **PowerShell as Administrator** and execute:  
```powershell
cd C:\IVR\Deployment
.\deploy-ivr.ps1 -all
```

This will:

- Install all prerequisites (VC++ Redistributable, Telnet, PostgreSQL, ODBC, Python, FFmpeg)  
- Copy application files into `C:\CreacodeSAS`  
- Restore the PostgreSQL database from backup  
- Install required Python libraries (`gTTS`, `pydub`)  
- Generate multilingual voice files and place them into the final `Voice/` directory  
- Configure and start the IVR Windows service with firewall rules  

### 3. Verify Deployment
After the script completes, verify the following:

- **Service:** Confirm the IVR service is running in Windows Services.  
- **Database:** Connect to PostgreSQL and check that the `creacodesas` database has been restored.  
- **Voice Files:** Ensure the `Voice/` directory contains the generated language folders (e.g., `english`, `turkish`, `german`).  
- **CLI:** Use Telnet to connect to the IVR runtime for configuration and monitoring:  
  ```bash
  telnet 127.0.0.1
  ```  
  *(default user: `a`, password: `a`)*  

**Repository Structure**

| Directory | Description |
|------------|-------------|
| `Bin/` | Executables and runtime binaries |
| `LOG/` | System logs (created during runtime) |
| `RadiusDictionary/` | RADIUS protocol dictionary files |
| `Record/` | Call recordings (created during runtime) |
| `Scripts/` | IVR call flow scripts and configuration logic |
| `Voice/` | Generated voice prompts (created during deployment) |

---

## Test Call Flow

To validate the installation, deploy a sample IVR script located under the `Scripts/` directory and place a SIP call to the system.  

A practical starting point is the demo service `Scripts\cc_info_service`, which implements a **credit card information inquiry** using RADIUS, direct database, or Web API access.

### Script Compilation
All IVR logic is written in a domain-specific scripting language and must be compiled before execution.  
Compilation is performed with the **SCC.exe** (Script Compiler) tool provided in the `Bin/` directory.  
Inside each service folder (for example, `Scripts\cc_info_service\Creacode`), a batch file named `SCC_comp.bat` compiles the source script:

```bat
..\..\Bin\SCC.exe Main.txt out.sc
pause
```

This generates the binary script file **`out.sc`**, which is automatically loaded by the IVR runtime either when the service starts or dynamically reloaded during operation without restarting the IVR service. Developers can modify script logic, recompile it instantly, and apply the new version to active call flows in real time.

---

### Main.txt – Entry Point
Defines global parameters, initializes the session, and sets the default language.  
Execution begins here when a call arrives.  
It provides shared functions such as language selection, RADIUS authentication, balance playback, and session control.

---

### NewSession.txt – Session Logic and Interaction
Implements the per-call interaction, handling SIP INVITE → DTMF data collection → account authentication.  
Supports multiple authentication paths (HTTP API, RADIUS, DB lookup, or fixed demo data).  
Uses `PlayAmount()` to announce retrieved balances and transfers callers to an agent when needed.

---

### Ringing.txt – Bridging to Live Agent
Handles SIP signaling while connecting the caller (LEG_A) to a human agent (LEG_B).  
Manages ringback tone, monitors call progress, and bridges both legs via SIP re-INVITE.  
Logs rejections and ends sessions gracefully.

---

### CallMonitor.txt – Call Supervision and Media Handling
Monitors the live bridged call:  
- Confirms connection and logs timestamps  
- Handles re-INVITE rejection or call drops  
- Passes in-call DTMF to the agent  
- Supports reconnecting the caller to IVR if needed  
- Finalizes sessions and CDRs  

Together, these four scripts demonstrate the full call lifecycle — from inbound SIP INVITE, through interactive authentication, to live-agent escalation and monitored teardown.

---

## Outbound Routing Configuration

When the IVR initiates a secondary call (**LEG_B**) — for example, to connect the caller with a local agent, office extension, or external trunk/SBC — the destination is determined by the **outbound routing configuration**.

Routing rules are managed dynamically through the **Telnet CLI** and are immediately applied at runtime without restarting the service.  
Configuration syntax and examples are documented in detail in:  
`DOC/CreacodeSAS_ConfigurationGuide.pdf`

### Route Command Syntax
```bash
route [print]
[add order_id=FV [cpn=FV] [dnis=FV] [source_ip_start=FV] [source_ip_end=FV]
 [rule=FV] [proxy_ip=FV] [proxy_port=FV] [domain_name=FV]]
[delete order_id=FV]
[update order_id=FV [cpn=FV] [dnis=FV] [source_ip_start=FV] [source_ip_end=FV]
 [rule=FV] [proxy_ip=FV] [proxy_port=FV] [domain_name=FV]]
[reload]
```

### Command Descriptions
- **print** — Displays all route rules in the current order.  
- **add** — Adds a new routing rule and reloads the route table.  
- **delete** — Deletes the route with the specified `order_id` and reloads the route table.  
- **update** — Updates an existing route using its `order_id`.  
- **reload** — Manually reloads the routing table into memory.  

### Parameter Descriptions
| Parameter | Description |
|------------|-------------|
| `order_id` | Unique route ID (required) |
| `cpn` | Calling party number pattern |
| `dnis` | Called party number pattern |
| `source_ip_start`, `source_ip_end` | IP address range for incoming calls |
| `rule` | Pattern translation or prefix rules to apply on destination numbers. Processed in order. Example: `0212=90212;0216=90216` |
| `proxy_ip` | Target SIP proxy or gateway IP address |
| `proxy_port` | SIP proxy port (default: `5060`) |
| `domain_name` | SIP domain to use for outbound registration or routing |

### Example Usage
```bash
route add order_id=2 cpn=90* dnis=90212* source_ip_start=192.168.1.1 \
source_ip_end=192.168.1.100 rule=90=0; proxy_ip=192.168.1.50 \
proxy_port=5060 domain_name=foo.com
```

This example adds a rule that:

- Matches calls where the calling number starts with `90` and the called number begins with `90212`  
- Limits the source IP range for incoming requests  
- Rewrites the prefix `90` to `0` before routing  
- Sends the call to proxy `192.168.1.50:5060` under the domain `foo.com`  

To update the proxy information later:
```bash
route update order_id=2 proxy_ip=192.168.1.55 proxy_port=5050
```

### Notes
- Routes are evaluated in ascending order of `order_id`.  
- After any `add`, `update`, or `delete`, the routing table is automatically reloaded.  
- Configuration changes are stored in the system database and remain active both after executing the `route reload` command at runtime and across full service restarts.

---

