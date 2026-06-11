import { useEffect, useMemo, useRef, useState } from "react";
import {
  checkBackendHealth,
  createShipment,
  getCustomers,
  getServiceStatus,
  getSalesByState,
  getSkuPerformance,
  getSkus,
  getStates,
  ingestSales,
  login,
  postTelemetryEvent,
  sendChatMessage
} from "./api";

const VALID_VOLUMES = [200, 400, 500, 750, 1000, 1500, 2000];
const CHAT_SQL_DEBUG_ENABLED = import.meta.env.VITE_CHATBOT_SQL_DEBUG_ENABLED === "1";
const CHAT_SQL_DEBUG_TOKEN = import.meta.env.VITE_CHATBOT_SQL_DEBUG_TOKEN || "";

function Login({ onLogin, error }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("password");

  async function submit(e) {
    e.preventDefault();
    await onLogin(username, password);
  }

  return (
    <div className="login-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <form className="card login-card" onSubmit={submit}>
        <h1>DRINKOO Control Room</h1>
        <p>Track SKU performance, sales, and shipments across India.</p>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error ? <div className="error">{error}</div> : null}
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
}

function StatCard({ title, value, hint }) {
  return (
    <div className="card stat-card">
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-hint">{hint}</div>
    </div>
  );
}

function formatMoney(v) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v || 0);
}

function StatusPage() {
  const [networkOnline, setNetworkOnline] = useState(typeof navigator !== "undefined" ? navigator.onLine : true);
  const [statusData, setStatusData] = useState(null);
  const [statusError, setStatusError] = useState("");
  const [lastCheckedAt, setLastCheckedAt] = useState("");

  useEffect(() => {
    function onOnline() {
      setNetworkOnline(true);
    }

    function onOffline() {
      setNetworkOnline(false);
    }

    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  useEffect(() => {
    async function loadStatus() {
      setLastCheckedAt(new Date().toLocaleTimeString());
      if (!networkOnline) {
        setStatusData(null);
        setStatusError("Browser is offline");
        return;
      }
      try {
        const data = await getServiceStatus();
        setStatusData(data);
        setStatusError("");
      } catch (err) {
        setStatusData(null);
        setStatusError(err?.message || "Status endpoint unavailable");
      }
    }

    loadStatus();
    const timer = setInterval(loadStatus, 15000);
    return () => clearInterval(timer);
  }, [networkOnline]);

  const apiOnline = Boolean(statusData && statusData.components?.api === "online");
  const dbOnline = Boolean(statusData && statusData.components?.database === "online");
  const appOnline = networkOnline && apiOnline && dbOnline;

  return (
    <div className="status-shell">
      <div className="status-card card">
        <h1>DRINKOO Status</h1>
        <p>Standalone service health page</p>
        <div className={`health-chip ${appOnline ? "online" : "offline"}`}>
          <span className="health-dot" />
          {appOnline ? "All Systems Operational" : "Service Disruption Detected"}
        </div>

        <div className="status-grid">
          <div className="status-item">
            <div className="status-label">Browser Network</div>
            <div className={`status-value ${networkOnline ? "online" : "offline"}`}>{networkOnline ? "Online" : "Offline"}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Backend API</div>
            <div className={`status-value ${apiOnline ? "online" : "offline"}`}>{apiOnline ? "Online" : "Offline"}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Database</div>
            <div className={`status-value ${dbOnline ? "online" : "offline"}`}>{dbOnline ? "Online" : "Offline"}</div>
          </div>
        </div>

        {statusError ? <div className="error">{statusError}</div> : null}
        {statusData?.database_error ? <div className="error">DB error: {statusData.database_error}</div> : null}
        <div className="status-meta">Last checked: {lastCheckedAt || "-"}</div>
      </div>
    </div>
  );
}

export default function App() {
  if (window.location.pathname === "/status") {
    return <StatusPage />;
  }

  const appSessionId = useMemo(() => {
    const existing = localStorage.getItem("drinkoo_observability_session");
    if (existing) {
      return existing;
    }
    const generated = `obs_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem("drinkoo_observability_session", generated);
    return generated;
  }, []);

  const clickLogRef = useRef({});

  const [token, setToken] = useState(localStorage.getItem("drinkoo_token"));
  const [loginError, setLoginError] = useState("");
  const [networkOnline, setNetworkOnline] = useState(typeof navigator !== "undefined" ? navigator.onLine : true);
  const [backendOnline, setBackendOnline] = useState(true);

  const [states, setStates] = useState([]);
  const [skus, setSkus] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [salesByState, setSalesByState] = useState([]);
  const [skuPerformance, setSkuPerformance] = useState([]);
  const [selectedStateId, setSelectedStateId] = useState("all");
  const [statusMessage, setStatusMessage] = useState("");

  const [newSale, setNewSale] = useState({ sku_id: "", state_id: "", quantity: 1, price: 20 });
  const [shipment, setShipment] = useState({ sku_id: "", quantity_units: 100, from_state_id: "", to_state_id: "" });

  const [newSku, setNewSku] = useState({
    flavor: "",
    name: "",
    category: "Soda",
    volume: 500,
    mfgCost: 10,
    shippingCost: 4,
    retailPrice: 25,
    active: true
  });

  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(localStorage.getItem("drinkoo_chat_session") || "");
  const [chatMessages, setChatMessages] = useState([
    {
      role: "assistant",
      text: "Hi, I can help with DRINKOO SKUs, flavors, and placing an order request."
    }
  ]);
  const [chatSqlDebug, setChatSqlDebug] = useState(false);

  const filteredSalesByState = useMemo(() => {
    if (selectedStateId === "all") {
      return salesByState;
    }
    return salesByState.filter((s) => String(s.state_id) === String(selectedStateId));
  }, [salesByState, selectedStateId]);

  function trackEvent(eventType, action, options = {}) {
    postTelemetryEvent({
      event_type: eventType,
      action,
      page: window.location.pathname,
      session_id: appSessionId,
      success: options.success !== false,
      error_code: options.errorCode,
      error_message: options.errorMessage,
      metadata: options.metadata || {}
    }).catch(() => {
      // Telemetry never blocks user actions.
    });
  }

  function handleUiClickCapture(e) {
    const target = e.target.closest("button, a, select, input[type='checkbox'], input[type='submit']");
    if (!target) {
      return;
    }
    const rawLabel =
      target.getAttribute("aria-label") ||
      target.textContent ||
      target.getAttribute("name") ||
      target.className ||
      target.tagName;
    const label = String(rawLabel).replace(/\s+/g, " ").trim().slice(0, 80) || "unknown";

    const key = `${target.tagName}:${label}`;
    const now = Date.now();
    const lastSeen = clickLogRef.current[key] || 0;
    if (now - lastSeen < 700) {
      return;
    }
    clickLogRef.current[key] = now;
    trackEvent("ui.click", "interact", {
      metadata: { element: target.tagName.toLowerCase(), label }
    });
  }

  async function loadDashboard() {
    trackEvent("journey.dashboard_load", "begin");
    const [stateData, skuData, customerData, stateSalesData, skuPerfData] = await Promise.all([
      getStates(),
      getSkus(),
      getCustomers(),
      getSalesByState(),
      getSkuPerformance()
    ]);
    setStates(stateData);
    setSkus(skuData);
    setCustomers(customerData);
    setSalesByState(stateSalesData);
    setSkuPerformance(skuPerfData);
    trackEvent("journey.dashboard_load", "complete", {
      metadata: {
        states: stateData.length,
        skus: skuData.length,
        customers: customerData.length
      }
    });
  }

  useEffect(() => {
    function setOnline() {
      setNetworkOnline(true);
      trackEvent("system.network", "online");
    }

    function setOffline() {
      setNetworkOnline(false);
      trackEvent("system.network", "offline", { success: false });
    }

    window.addEventListener("online", setOnline);
    window.addEventListener("offline", setOffline);
    return () => {
      window.removeEventListener("online", setOnline);
      window.removeEventListener("offline", setOffline);
    };
  }, []);

  useEffect(() => {
    async function pingBackend() {
      if (!networkOnline) {
        setBackendOnline(false);
        return;
      }
      try {
        await checkBackendHealth();
        setBackendOnline(true);
      } catch {
        setBackendOnline(false);
      }
    }

    pingBackend();
    const timer = setInterval(pingBackend, 15000);
    return () => clearInterval(timer);
  }, [networkOnline]);

  useEffect(() => {
    if (!token) {
      return;
    }

    loadDashboard().catch((e) => {
      setStatusMessage(`Failed to load dashboard: ${e.message}`);
      trackEvent("journey.dashboard_load", "failed", {
        success: false,
        errorCode: "dashboard_load_failed",
        errorMessage: e.message
      });
    });
  }, [token]);

  async function handleLogin(username, password) {
    try {
      setLoginError("");
      const result = await login(username, password);
      localStorage.setItem("drinkoo_token", result.access_token);
      setToken(result.access_token);
      trackEvent("journey.login", "success", { metadata: { username } });
    } catch {
      setLoginError("Invalid credentials. Use admin/password in non-production.");
      trackEvent("journey.login", "failed", {
        success: false,
        errorCode: "invalid_credentials"
      });
    }
  }

  function logout() {
    trackEvent("journey.logout", "click");
    localStorage.removeItem("drinkoo_token");
    setToken(null);
  }

  async function submitChat(e) {
    e.preventDefault();
    const text = chatInput.trim();
    if (!text || chatLoading) {
      return;
    }

    setChatMessages((prev) => [...prev, { role: "user", text }]);
    setChatInput("");
    setChatLoading(true);
    trackEvent("journey.chat", "message_sent", { metadata: { length: text.length } });

    try {
      const result = await sendChatMessage(text, chatSessionId || null, {
        debugSql: CHAT_SQL_DEBUG_ENABLED && chatSqlDebug,
        debugToken: CHAT_SQL_DEBUG_ENABLED ? CHAT_SQL_DEBUG_TOKEN : ""
      });
      if (result.session_id && result.session_id !== chatSessionId) {
        setChatSessionId(result.session_id);
        localStorage.setItem("drinkoo_chat_session", result.session_id);
      }
      const suffix =
        typeof result.remaining_messages === "number"
          ? ` (remaining: ${result.remaining_messages})`
          : "";
      const debugSqlText = result.debug?.sql ? `\nSQL: ${result.debug.sql}` : "";
      const failureSignature =
        String(result.reply || "").includes("I could not find") ||
        String(result.reply || "").includes("I can only answer") ||
        String(result.reply || "").includes("supports up to 4 messages");
      trackEvent("journey.chat", failureSignature ? "message_handled_with_limit" : "message_handled", {
        success: !failureSignature,
        errorCode: failureSignature ? "chat_limited_or_no_answer" : undefined
      });
      setChatMessages((prev) => [...prev, { role: "assistant", text: `${result.reply}${suffix}${debugSqlText}` }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: "assistant", text: "Chat is temporarily unavailable. Please try again." }]);
      trackEvent("journey.chat", "request_failed", {
        success: false,
        errorCode: "chat_request_failed",
        errorMessage: err?.message || "unknown"
      });
    } finally {
      setChatLoading(false);
    }
  }

  async function submitSale(e) {
    e.preventDefault();
    try {
      setStatusMessage("Recording sale...");
      await ingestSales([
        {
          sku_id: newSale.sku_id,
          customer_id: null,
          state_id: Number(newSale.state_id),
          quantity_units: Number(newSale.quantity),
          price: Number(newSale.price),
          transaction_date: null
        }
      ]);
      setStatusMessage("Sale recorded.");
      await loadDashboard();
      trackEvent("journey.sale", "submit_success", {
        metadata: {
          sku_id: newSale.sku_id,
          state_id: newSale.state_id,
          quantity: Number(newSale.quantity)
        }
      });
    } catch (e2) {
      setStatusMessage(`Sale ingestion failed: ${e2.message}`);
      trackEvent("journey.sale", "submit_failed", {
        success: false,
        errorCode: "sale_ingest_failed",
        errorMessage: e2.message
      });
    }
  }

  async function submitShipment(e) {
    e.preventDefault();
    try {
      setStatusMessage("Creating shipment...");
      const response = await createShipment({
        sku_id: shipment.sku_id,
        quantity_units: Number(shipment.quantity_units),
        from_state_id: Number(shipment.from_state_id),
        to_state_id: Number(shipment.to_state_id)
      });
      setStatusMessage(`Shipment created. ID: ${response.shipment_id}`);
      trackEvent("journey.shipment", "submit_success", {
        metadata: {
          sku_id: shipment.sku_id,
          from_state_id: shipment.from_state_id,
          to_state_id: shipment.to_state_id
        }
      });
    } catch (e2) {
      setStatusMessage(`Shipment failed: ${e2.message}`);
      trackEvent("journey.shipment", "submit_failed", {
        success: false,
        errorCode: "shipment_create_failed",
        errorMessage: e2.message
      });
    }
  }

  function previewSku() {
    const margin = Number(newSku.retailPrice) - Number(newSku.mfgCost) - Number(newSku.shippingCost);
    const valid = VALID_VOLUMES.includes(Number(newSku.volume));
    return valid
      ? `Estimated unit margin: ${formatMoney(margin)} | Size: ${newSku.volume}ml`
      : "Invalid volume. Allowed: 200, 400, 500, 750, 1000, 1500, 2000 ml";
  }

  if (!token) {
    return <Login onLogin={handleLogin} error={loginError} />;
  }

  const totalRevenue = filteredSalesByState.reduce((acc, x) => acc + (x.revenue || 0), 0);
  const totalUnits = filteredSalesByState.reduce((acc, x) => acc + (x.units || 0), 0);
  const appOnline = networkOnline && backendOnline;

  return (
    <div className="app-shell" onClickCapture={handleUiClickCapture}>
      <header className="topbar">
        <div>
          <h1>DRINKOO Dashboard</h1>
          <p>State-wise sales, SKU management and shipment orchestration</p>
          <div className={`health-chip ${appOnline ? "online" : "offline"}`}>
            <span className="health-dot" />
            {appOnline ? "App Online" : "App Offline"}
          </div>
        </div>
        <div className="topbar-actions">
          <select value={selectedStateId} onChange={(e) => setSelectedStateId(e.target.value)}>
            <option value="all">All States / UTs</option>
            {states.map((s) => (
              <option key={s.state_id} value={s.state_id}>
                {s.state_name}
              </option>
            ))}
          </select>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <section className="stats-grid">
        <StatCard title="States Covered" value={states.length} hint="All India coverage" />
        <StatCard title="Customers" value={customers.length} hint="Active accounts" />
        <StatCard title="Revenue" value={formatMoney(totalRevenue)} hint="Filtered state scope" />
        <StatCard title="Units Sold" value={totalUnits} hint="Across selected period" />
      </section>

      <section className="grid-two">
        <div className="card panel">
          <h2>SKU Performance</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Units</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {skuPerformance.slice(0, 10).map((row) => (
                  <tr key={row.sku_id}>
                    <td>{row.sku_name}</td>
                    <td>{row.units_sold}</td>
                    <td>{formatMoney(row.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card panel">
          <h2>Sales by State</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>State</th>
                  <th>Units</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {filteredSalesByState.slice(0, 12).map((row) => (
                  <tr key={row.state_id}>
                    <td>{row.state_name}</td>
                    <td>{row.units}</td>
                    <td>{formatMoney(row.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="grid-two">
        <form className="card panel" onSubmit={submitSale}>
          <h2>Record Sale (ETL Input)</h2>
          <label>
            SKU
            <select required value={newSale.sku_id} onChange={(e) => setNewSale({ ...newSale, sku_id: e.target.value })}>
              <option value="">Select SKU</option>
              {skus.map((s) => (
                <option key={s.sku_id} value={s.sku_id}>
                  {s.sku_name}
                </option>
              ))}
            </select>
          </label>
          <label>
            State
            <select required value={newSale.state_id} onChange={(e) => setNewSale({ ...newSale, state_id: e.target.value })}>
              <option value="">Select state</option>
              {states.map((s) => (
                <option key={s.state_id} value={s.state_id}>
                  {s.state_name}
                </option>
              ))}
            </select>
          </label>
          <div className="row-2">
            <label>
              Quantity
              <input type="number" min="1" value={newSale.quantity} onChange={(e) => setNewSale({ ...newSale, quantity: e.target.value })} />
            </label>
            <label>
              Unit Price
              <input type="number" min="0" step="0.01" value={newSale.price} onChange={(e) => setNewSale({ ...newSale, price: e.target.value })} />
            </label>
          </div>
          <button type="submit">Submit Sale</button>
        </form>

        <form className="card panel" onSubmit={submitShipment}>
          <h2>Create Shipment</h2>
          <label>
            SKU
            <select required value={shipment.sku_id} onChange={(e) => setShipment({ ...shipment, sku_id: e.target.value })}>
              <option value="">Select SKU</option>
              {skus.map((s) => (
                <option key={s.sku_id} value={s.sku_id}>
                  {s.sku_name}
                </option>
              ))}
            </select>
          </label>
          <div className="row-2">
            <label>
              From State
              <select required value={shipment.from_state_id} onChange={(e) => setShipment({ ...shipment, from_state_id: e.target.value })}>
                <option value="">From</option>
                {states.map((s) => (
                  <option key={s.state_id} value={s.state_id}>
                    {s.state_name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              To State
              <select required value={shipment.to_state_id} onChange={(e) => setShipment({ ...shipment, to_state_id: e.target.value })}>
                <option value="">To</option>
                {states.map((s) => (
                  <option key={s.state_id} value={s.state_id}>
                    {s.state_name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            Quantity
            <input type="number" min="1" value={shipment.quantity_units} onChange={(e) => setShipment({ ...shipment, quantity_units: e.target.value })} />
          </label>
          <button type="submit">Create Shipment</button>
        </form>
      </section>

      <section className="grid-one">
        <div className="card panel">
          <h2>SKU Form Preview (Validation Focus)</h2>
          <div className="row-3">
            <label>
              Flavor Profile
              <input value={newSku.flavor} onChange={(e) => setNewSku({ ...newSku, flavor: e.target.value })} />
            </label>
            <label>
              Product Name
              <input value={newSku.name} onChange={(e) => setNewSku({ ...newSku, name: e.target.value })} />
            </label>
            <label>
              Category
              <select value={newSku.category} onChange={(e) => setNewSku({ ...newSku, category: e.target.value })}>
                <option>Soda</option>
                <option>Energy Drinks</option>
                <option>Fruit Juices</option>
                <option>Iced Tea</option>
                <option>Sparkling Water</option>
                <option>Health Drinks</option>
                <option>Regional/Special</option>
              </select>
            </label>
          </div>
          <div className="row-3">
            <label>
              Volume (ml)
              <select value={newSku.volume} onChange={(e) => setNewSku({ ...newSku, volume: Number(e.target.value) })}>
                {VALID_VOLUMES.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Manufacturing Cost
              <input type="number" min="0" step="0.01" value={newSku.mfgCost} onChange={(e) => setNewSku({ ...newSku, mfgCost: e.target.value })} />
            </label>
            <label>
              Shipping Cost
              <input type="number" min="0" step="0.01" value={newSku.shippingCost} onChange={(e) => setNewSku({ ...newSku, shippingCost: e.target.value })} />
            </label>
          </div>
          <div className="row-2">
            <label>
              Suggested Retail Price
              <input type="number" min="0" step="0.01" value={newSku.retailPrice} onChange={(e) => setNewSku({ ...newSku, retailPrice: e.target.value })} />
            </label>
            <label className="checkbox-row">
              <input type="checkbox" checked={newSku.active} onChange={(e) => setNewSku({ ...newSku, active: e.target.checked })} />
              Active
            </label>
          </div>
          <div className="preview-box">{previewSku()}</div>
        </div>
      </section>

      {statusMessage ? <div className="toast">{statusMessage}</div> : null}

      <button
        className="chat-toggle"
        onClick={() => {
          const next = !chatOpen;
          setChatOpen(next);
          trackEvent("journey.chat", next ? "open" : "close");
        }}
      >
        {chatOpen ? "Close Chat" : "Chat with DRINKOO"}
      </button>

      {chatOpen ? (
        <div className="chat-window card">
          <div className="chat-header">DRINKOO Assistant</div>
          {CHAT_SQL_DEBUG_ENABLED ? (
            <div className="chat-debug-row">
              <label className="chat-debug-toggle">
                <input
                  type="checkbox"
                  checked={chatSqlDebug}
                  onChange={(e) => setChatSqlDebug(e.target.checked)}
                />
                SQL debug (admin only)
              </label>
            </div>
          ) : null}
          <div className="chat-body">
            {chatMessages.map((m, idx) => (
              <div key={`${m.role}-${idx}`} className={`chat-msg ${m.role}`}>
                {m.text}
              </div>
            ))}
          </div>
          <form className="chat-form" onSubmit={submitChat}>
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask about flavors, SKU, or order"
              maxLength={400}
            />
            <button type="submit" disabled={chatLoading}>
              {chatLoading ? "..." : "Send"}
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
