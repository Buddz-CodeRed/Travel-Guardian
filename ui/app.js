// Step 7: what happens when you click things in the window.
// window.pywebview.api.<name>() runs the matching Python method in app.py.

const consentScreen = document.getElementById("consent-screen");
const resultsScreen = document.getElementById("results-screen");
const consentBox = document.getElementById("consent-box");
const scanButton = document.getElementById("scan-button");
const scanHint = document.getElementById("scan-hint");
const notice = document.getElementById("notice");

// Show one screen and hide the others.
function showScreen(screen) {
    for (const s of [consentScreen, resultsScreen]) {
        s.hidden = s !== screen;
    }
}

// Fill a list with text items. textContent is used (not innerHTML)
// so nothing from the network can be run as code.
function fillList(listElement, items) {
    listElement.innerHTML = "";
    for (const text of items) {
        const li = document.createElement("li");
        li.textContent = text;
        listElement.appendChild(li);
    }
}

// When pywebview is ready, show the Wi-Fi name on the consent screen.
window.addEventListener("pywebviewready", async () => {
    const name = await window.pywebview.api.get_wifi_name();
    document.getElementById("network-name").textContent = name;
});

// The Scan button only works after the consent box is ticked.
consentBox.addEventListener("change", () => {
    scanButton.disabled = !consentBox.checked;
});

// Switch the first screen in or out of its "scanning" look.
// The class "is-scanning" is what style.css uses to hide the card
// and spin the ring around the button.
function setScanning(isScanning) {
    consentScreen.classList.toggle("is-scanning", isScanning);
    scanButton.textContent = isScanning ? "Scanning" : "Scan";
    scanHint.textContent = isScanning ? "This takes about 30 seconds." : "";
    // Disabled while scanning so it can't be clicked twice.
    scanButton.disabled = isScanning || !consentBox.checked;
}

async function runScan() {
    notice.textContent = "";
    showScreen(consentScreen);      // "Scan again" starts from the results screen
    setScanning(true);
    const results = await window.pywebview.api.scan();
    setScanning(false);

    if (results.error) {
        notice.textContent = results.error;
        return;
    }
    showResults(results);
}

function showResults(results) {
    // Status badge: colour and words come from the overall risk.
    const badge = document.getElementById("status-badge");
    badge.className = "status risk-" + results.overall;
    document.getElementById("status-text").textContent = results.overall;

    document.getElementById("summary").textContent = results.summary;

    // Advice: only from Medium and High findings, without repeats.
    const advice = [];
    for (const f of results.findings) {
        if (f.risk !== "Low" && !advice.includes(f.advice)) {
            advice.push(f.advice);
        }
    }
    if (advice.length === 0) advice.push("No action needed.");
    fillList(document.getElementById("advice-list"), advice);

    fillList(document.getElementById("message-list"), results.messages);

    // Details: every finding with its risk level, plus the raw Wi-Fi facts.
    fillList(
        document.getElementById("findings-list"),
        results.findings.map((f) => `${f.title} (${f.risk})`)
    );
    // Devices found: the router, this laptop, then everyone else.
    const d = results.discovery;
    const devices = [];
    if (d.router_found) devices.push(`${results.network.gateway} (router)`);
    devices.push(`${results.network.ip} (this laptop)`);
    for (const ip of d.other_devices) devices.push(ip);
    fillList(document.getElementById("device-list"), devices);

    const w = results.wifi;
    document.getElementById("wifi-details").textContent =
        `Wi-Fi security: ${w.authentication || "unknown"} (${w.cipher || "-"}), signal ${w.signal ?? "-"}%. ` +
        `Router found: ${results.discovery.router_found ? "yes" : "no"}. ` +
        `Windows network type: ${results.protection.profile || "unknown"}, ` +
        `firewall ${results.protection.firewall_on ? "on" : "off"}.`;

    showScreen(resultsScreen);
}

scanButton.addEventListener("click", runScan);
document.getElementById("again-button").addEventListener("click", runScan);

document.getElementById("details-button").addEventListener("click", (event) => {
    const details = document.getElementById("details");
    details.hidden = !details.hidden;
    event.target.textContent = details.hidden ? "Show details" : "Hide details";
});

document.getElementById("clear-button").addEventListener("click", async () => {
    await window.pywebview.api.clear_session();
    consentBox.checked = false;
    scanButton.disabled = true;
    showScreen(consentScreen);
    notice.textContent = "Session data cleared.";
});