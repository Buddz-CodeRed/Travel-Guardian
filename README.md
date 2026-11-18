# Travel Guardian

A Windows desktop widget that checks the Wi-Fi network you are connected to and explains the security risks in plain English, using an offline AI model. Built for COMP.6207 Special Topic.

## Just want to use it?
Download `TravelGuardian.zip` from this repository's **Releases** page, extract it, double-click `Setup.bat` once (installs Nmap), then right-click `TravelGuardian.exe` > Run as administrator. Full steps are in `INSTALL.txt`. Python is not needed.

## Run from the source code
1. Install [Nmap](https://nmap.org/download.html) for Windows (includes Npcap), or double-click `Setup.bat`.
2. Create a virtual environment with Python 3.12 and install the requirements.
   The extra index gives a prebuilt llama-cpp-python, so no C++ compiler is needed:
   ```
   py -3.12 -m venv tg_env
   tg_env\Scripts\activate
   pip install -r requirements.txt --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
   ```
3. Download the AI model (about 800 MB) into `models/`, keeping this exact file name:
   [Llama-3.2-1B-Instruct-Q4_K_M.gguf](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf)
   (Without it the app still works and shows standard advice.)
4. Run: `python app.py`
5. Tests: `python -m pytest tests`

## Build the .exe
Run `build_exe.bat` (takes a few minutes). It makes `dist\TravelGuardian\` and `dist\TravelGuardian.zip`.

The AI model is Llama 3.2, licensed under the Llama 3.2 Community License (see `models/LICENSE.txt` and `models/NOTICE.txt`). Built with Llama.

Only scan networks you are authorised to scan.
