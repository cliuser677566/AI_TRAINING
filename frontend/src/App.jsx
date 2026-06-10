import { useEffect, useMemo, useState } from "react";
import {
  createShipment,
  getCustomers,
  getSalesByState,
  getSkuPerformance,
  getSkus,
  getStates,
  ingestSales,
  login
} from "./api";

const VALID_VOLUMES = [200, 400, 500, 750, 1000, 1500, 2000];

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

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("drinkoo_token"));
  const [loginError, setLoginError] = useState("");

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

  const filteredSalesByState = useMemo(() => {
    if (selectedStateId === "all") {
      return salesByState;
    }
    return salesByState.filter((s) => String(s.state_id) === String(selectedStateId));
  }, [salesByState, selectedStateId]);

  async function loadDashboard() {
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
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    loadDashboard().catch((e) => {
      setStatusMessage(`Failed to load dashboard: ${e.message}`);
    });
  }, [token]);

  async function handleLogin(username, password) {
    try {
      setLoginError("");
      const result = await login(username, password);
      localStorage.setItem("drinkoo_token", result.access_token);
      setToken(result.access_token);
    } catch {
      setLoginError("Invalid credentials. Use admin/password in non-production.");
    }
  }

  function logout() {
    localStorage.removeItem("drinkoo_token");
    setToken(null);
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
    } catch (e2) {
      setStatusMessage(`Sale ingestion failed: ${e2.message}`);
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
    } catch (e2) {
      setStatusMessage(`Shipment failed: ${e2.message}`);
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

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>DRINKOO Dashboard</h1>
          <p>State-wise sales, SKU management and shipment orchestration</p>
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
    </div>
  );
}
