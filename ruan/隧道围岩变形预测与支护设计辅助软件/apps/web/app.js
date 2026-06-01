const state = {
  token: localStorage.getItem("tunnel_token") || "",
  user: null,
  dashboard: null,
  sections: [],
  selectedSection: null,
  predictions: [],
  recommendations: [],
  alerts: [],
  contracts: null,
  filters: {
    keyword: "",
    risk: "",
  },
  scenario: {
    sectionId: "SEC-005",
    scenarioName: "甯歌鎺ㄨ繘鎯呮櫙",
    excavationIntensity: 1.0,
    rainfallFactor: 0.5,
    safetyFactor: 1.15,
  },
};

const loginPanel = document.querySelector("#login-panel");
const appShell = document.querySelector("#app-shell");
const contentArea = document.querySelector("#content-area");
const userPill = document.querySelector("#user-pill");
const loginMessage = document.querySelector("#login-message");
const loginForm = document.querySelector("#login-form");
const logoutBtn = document.querySelector("#logout-btn");
const navLinks = [...document.querySelectorAll(".sidenav a")];

function route() {
  return window.location.hash.replace("#", "") || "dashboard";
}

function setActiveNav() {
  const current = route();
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.route === current);
  });
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }
  const response = await fetch(path, {
    ...options,
    headers,
  });
  const data = await response.json();
  if (response.status === 401) {
    resetSession();
  }
  if (!response.ok || !data.ok) {
    throw new Error(data.message || "璇锋眰澶辫触");
  }
  return data;
}

function resetSession() {
  state.token = "";
  state.user = null;
  localStorage.removeItem("tunnel_token");
  loginPanel.classList.remove("hidden");
  appShell.classList.add("hidden");
}

function riskClass(level) {
  return (level || "").toLowerCase();
}

function riskLabel(level) {
  const map = {
    LOW: "浣庨闄?,
    MEDIUM: "涓闄?,
    HIGH: "楂橀闄?,
    CRITICAL: "涓寸晫椋庨櫓",
  };
  return map[level] || level;
}

function formatNumber(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function metricRow(label, value, unit = "") {
  return `<div class="metric-row"><span>${label}</span><strong>${value}${unit}</strong></div>`;
}

function riskPill(level, score) {
  return `<span class="risk-pill ${riskClass(level)}">${riskLabel(level)}${score ? ` 路 ${formatNumber(score)}` : ""}</span>`;
}

function buildPolyline(values, width, height, color) {
  const padding = 18;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = Math.max(max - min, 1);
  const step = (width - padding * 2) / Math.max(values.length - 1, 1);
  const points = values
    .map((value, index) => {
      const x = padding + step * index;
      const y = height - padding - ((value - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");
  return `<polyline fill="none" stroke="${color}" stroke-width="3" points="${points}" />`;
}

function renderPredictionChart(prediction) {
  if (!prediction) {
    return `<div class="empty-state">灏氭湭鐢熸垚棰勬祴缁撴灉銆傝閫夋嫨鍖烘骞舵墽琛岃绠椼€?/div>`;
  }
  const settlement = prediction.predictedSettlement;
  const convergence = prediction.predictedConvergence;
  return `
    <div class="chart-shell">
      <svg viewBox="0 0 720 220" role="img" aria-label="鍥村博棰勬祴瓒嬪娍鍥?>
        <rect x="0" y="0" width="720" height="220" fill="transparent"></rect>
        <line x1="18" y1="188" x2="702" y2="188" stroke="rgba(255,255,255,0.18)" />
        <line x1="18" y1="18" x2="18" y2="188" stroke="rgba(255,255,255,0.18)" />
        ${buildPolyline(settlement, 720, 220, "#ff8a3d")}
        ${buildPolyline(convergence, 720, 220, "#58d0db")}
      </svg>
      <div class="chart-legend">
        <span class="legend-settlement">鎷遍《娌夐檷棰勬祴</span>
        <span class="legend-convergence">鍛ㄨ竟鏀舵暃棰勬祴</span>
      </div>
    </div>
  `;
}

function statusTable(rows) {
  return `
    <table class="section-table">
      <thead>
        <tr>
          <th>鍖烘</th>
          <th>鍥村博绾у埆</th>
          <th>椋庨櫓</th>
          <th>娌夐檷 mm</th>
          <th>鏀舵暃 mm</th>
          <th>鎷辨灦搴斿姏 kN</th>
          <th>鏃ュ閲?mm</th>
        </tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) => `
            <tr data-section-id="${row.id}" class="section-row">
              <td>${row.zone}</td>
              <td>${row.rockGrade}</td>
              <td>${riskPill(row.riskLevel, row.riskScore)}</td>
              <td>${formatNumber(row.settlement)}</td>
              <td>${formatNumber(row.convergence)}</td>
              <td>${formatNumber(row.archStress)}</td>
              <td>${formatNumber(row.delta)}</td>
            </tr>
          `,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderDashboard() {
  const dashboard = state.dashboard;
  if (!dashboard) {
    return `<div class="empty-state">鎬昏鏁版嵁灏氭湭鍔犺浇銆?/div>`;
  }
  return `
    <div class="view-header">
      <div>
        <h2>鎬昏闈㈡澘</h2>
        <p>鑱氱劍娌夐檷銆佹敹鏁涖€佹敮鎶ら棴鍚堟椂宸笌楂橀闄╁尯娈碉紝閫傚悎鐝墠浼氫笌璁捐澶嶆牳鑱斿腑浼氱洿鎺ユ姇灞忋€?/p>
      </div>
      <div class="meta-list">
        <span>${dashboard.projectName}</span>
        <span>${dashboard.siteName}</span>
        <span>鍒锋柊鑷郴缁熷疄鏃惰绠?/span>
      </div>
    </div>
    <div class="stats-grid">
      <article class="card stat-card">
        <h3>鐩戞祴鍖烘</h3>
        <strong>${dashboard.totalSections}</strong>
        <span>宸叉帴鍏ュ洿宀╁彉褰㈠簭鍒?/span>
      </article>
      <article class="card stat-card">
        <h3>楂橀闄╂</h3>
        <strong>${dashboard.highRiskSections}</strong>
        <span>闇€浼氬晢鎴栧鏍哥殑鍖烘</span>
      </article>
      <article class="card stat-card">
        <h3>骞冲潎椋庨櫓鍒?/h3>
        <strong>${formatNumber(dashboard.averageRiskScore)}</strong>
        <span>鎸夊洿宀┿€佸瘜姘淬€侀€熺巼鍜岄棴鍚堟椂宸患鍚堣绠?/span>
      </article>
      <article class="card stat-card">
        <h3>鏈€澶ф敹鏁?/h3>
        <strong>${formatNumber(dashboard.maxConvergence)}</strong>
        <span>鐢ㄤ簬鍒ゆ柇鏀姢鍌ㄥ鏄惁琚揩閫熸秷鑰?/span>
      </article>
    </div>
    <div class="split-grid">
      <article class="card table-card">
        <h3>鍖烘椋庨櫓鐑〃</h3>
        <p>鍗曞嚮浠讳竴鍖烘鍙烦杞埌璇︾粏鍙拌处鏌ョ湅鐩戞祴搴忓垪涓庡綋鍓嶅缓璁€?/p>
        ${statusTable(dashboard.statusBoard)}
      </article>
      <article class="card panel-card">
        <h3>棰勮鎽樿</h3>
        <div class="timeline">
          ${dashboard.alerts
            .map(
              (item) => `
                <div class="timeline-item">
                  <strong>${item.sectionName} 路 ${riskLabel(item.riskLevel)}</strong>
                  <div>${item.trigger}</div>
                  <div>${item.action}</div>
                </div>
              `,
            )
            .join("")}
        </div>
        <div class="footer-note">椋庨櫓鍒嗘槸棰勬祴鍓嶇殑鐜扮姸鍒嗗€硷紱鍦ㄢ€滃彉褰㈤娴嬧€濆拰鈥滄敮鎶ゅ鏍糕€濋〉闈㈠彲鐪嬪埌鎯呮櫙鍙犲姞鍚庣殑璁捐寤鸿銆?/div>
      </article>
    </div>
  `;
}

function sectionOptions() {
  return state.sections
    .map((section) => `<option value="${section.id}">${section.zone} / ${section.rockGrade} 绾?/ ${riskLabel(section.riskLevel)}</option>`)
    .join("");
}

function sectionDetail(section) {
  if (!section) {
    return `<div class="empty-state">璇烽€夋嫨宸︿晶鍖烘鏌ョ湅鏄庣粏銆?/div>`;
  }
  const records = section.monitoring.slice(-5).reverse();
  return `
    <div class="card panel-card">
      <h3>${section.name}</h3>
      <p>${section.geologyNote}</p>
      <div class="detail-grid">
        <div><dt>鍥村博绾у埆</dt><dd>${section.rockGrade}</dd></div>
        <div><dt>鍩嬫繁</dt><dd>${section.burialDepth} m</dd></div>
        <div><dt>鍦颁笅姘?/dt><dd>${section.groundwaterLevel}</dd></div>
        <div><dt>闂悎鏃跺樊</dt><dd>${section.supportClosureHours} h</dd></div>
        <div><dt>椋庨櫓鍒?/dt><dd>${formatNumber(section.riskScore)}</dd></div>
        <div><dt>椋庨櫓绛夌骇</dt><dd>${riskLabel(section.riskLevel)}</dd></div>
      </div>
      <h3 style="margin-top: 18px;">杩?5 娆＄洃娴?/h3>
      <table class="section-table">
        <thead>
          <tr>
            <th>鏃ユ湡</th>
            <th>娌夐檷</th>
            <th>鏀舵暃</th>
            <th>鎷辨灦搴斿姏</th>
            <th>渚у閫熺巼</th>
          </tr>
        </thead>
        <tbody>
          ${records
            .map(
              (item) => `
                <tr>
                  <td>${item.date}</td>
                  <td>${formatNumber(item.crownSettlement)}</td>
                  <td>${formatNumber(item.convergence)}</td>
                  <td>${formatNumber(item.archStress)}</td>
                  <td>${formatNumber(item.sideWallRate)}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
      <div class="callout">${section.controlPoints.join("锛?)}</div>
    </div>
  `;
}

function renderSections() {
  return `
    <div class="view-header">
      <div>
        <h2>鍖烘鍙拌处</h2>
        <p>鎶婂洿宀╃骇鍒€佸煁娣便€佸瘜姘淬€佺洃娴嬪簭鍒楀拰鍒濇湡鏀姢鍙傛暟鏀惧埌鍚屼竴涓搷浣滈潰鏉匡紝閬垮厤浜哄伐鍒囪〃姣斿銆?/p>
      </div>
      <div class="meta-list">
        <span>鍖烘鏁?${state.sections.length}</span>
        <span>鏁版嵁婧愶細鍐呯疆婕旂ず鐩戞祴搴?/span>
      </div>
    </div>
    <div class="filter-bar">
      <input id="keyword-input" type="text" placeholder="鎸夊尯娈点€侀噷绋嬫垨鍥村博绾у埆妫€绱? value="${state.filters.keyword}" />
      <select id="risk-select">
        <option value="">鍏ㄩ儴椋庨櫓</option>
        <option value="LOW" ${state.filters.risk === "LOW" ? "selected" : ""}>浣庨闄?/option>
        <option value="MEDIUM" ${state.filters.risk === "MEDIUM" ? "selected" : ""}>涓闄?/option>
        <option value="HIGH" ${state.filters.risk === "HIGH" ? "selected" : ""}>楂橀闄?/option>
        <option value="CRITICAL" ${state.filters.risk === "CRITICAL" ? "selected" : ""}>涓寸晫椋庨櫓</option>
      </select>
      <button class="primary-button" id="filter-btn" type="button">绛涢€?/button>
    </div>
    <div class="split-grid">
      <article class="card table-card">
        <h3>鍖烘鍒楄〃</h3>
        ${statusTable(state.sections)}
      </article>
      ${sectionDetail(state.selectedSection)}
    </div>
  `;
}

function renderAnalysis() {
  const latestPrediction = state.predictions[0];
  return `
    <div class="view-header">
      <div>
        <h2>鍙樺舰棰勬祴</h2>
        <p>鍩轰簬杩?4 娆＄洃娴嬭秼鍔裤€佸洿宀╁垎绾с€佹柦宸ユ壈鍔ㄣ€侀檷闆ㄦ斁澶т笌鏀姢闂悎鏃跺樊锛岃緭鍑?7 澶╄秼鍔夸笌椋庨櫓鍗囩骇鍒ゆ柇銆?/p>
      </div>
      <div class="meta-list">
        <span>妯″瀷锛氳秼鍔垮鎺?+ 椋庨櫓鍔犳潈</span>
        <span>缁撴灉鐢ㄤ簬璁捐浼氬晢锛屼笉鏇夸唬鐜板満澶嶆祴</span>
      </div>
    </div>
    <div class="card panel-card">
      <div class="scenario-grid">
        <label>
          鍖烘
          <select id="scenario-section">${sectionOptions()}</select>
        </label>
        <label>
          鎯呮櫙鍚嶇О
          <input id="scenario-name" type="text" value="${state.scenario.scenarioName}" />
        </label>
        <label>
          寮€鎸栨壈鍔ㄧ郴鏁?          <input id="scenario-excavation" type="number" min="0.8" max="1.6" step="0.05" value="${state.scenario.excavationIntensity}" />
        </label>
        <label>
          闄嶉洦鏀惧ぇ绯绘暟
          <input id="scenario-rainfall" type="number" min="0" max="1.5" step="0.05" value="${state.scenario.rainfallFactor}" />
        </label>
      </div>
      <div class="scenario-grid" style="margin-top: 14px;">
        <label>
          瀹夊叏鎶樺噺绯绘暟
          <input id="scenario-safety" type="number" min="0.8" max="1.4" step="0.05" value="${state.scenario.safetyFactor}" />
        </label>
        <div class="scenario-actions">
          <button class="primary-button" id="predict-btn" type="button">鎵ц棰勬祴</button>
          <button class="ghost-button" id="load-critical-btn" type="button">杞藉叆楂橀闄╃ず渚?/button>
        </div>
      </div>
      ${renderPredictionChart(latestPrediction)}
      ${
        latestPrediction
          ? `
            <div class="comparison-grid">
              <div class="card">
                <h3>棰勬祴缁撴灉鎽樿</h3>
                ${metricRow("鍖烘", latestPrediction.sectionName)}
                ${metricRow("椋庨櫓绛夌骇", riskLabel(latestPrediction.riskLevel))}
                ${metricRow("椋庨櫓鍒?, formatNumber(latestPrediction.riskScore))}
                ${metricRow("鎺ㄨ崘鏀姢绾у埆", latestPrediction.recommendedSupportLevel)}
                ${metricRow("鏃ュ闀垮熀鍊?, formatNumber(latestPrediction.trendIncrement), " mm")}
              </div>
              <div class="card">
                <h3>澶勭疆鎻愮ず</h3>
                <ul class="bullet-list">${latestPrediction.notes.map((note) => `<li>${note}</li>`).join("")}</ul>
              </div>
            </div>
          `
          : ""
      }
    </div>
  `;
}

function renderDesigns() {
  const latestRecommendation = state.recommendations[0];
  return `
    <div class="view-header">
      <div>
        <h2>鏀姢澶嶆牳</h2>
        <p>灏嗛娴嬬粨鏋滅洿鎺ユ槧灏勫埌鍠峰皠娣峰嚌鍦熷帤搴︺€侀敋鏉嗛暱搴︺€佹嫳鏋堕棿璺濅笌棰勭暀鍙樺舰閲忥紝褰㈡垚鍙惤鍦扮殑鏀姢澶嶆牳鎰忚銆?/p>
      </div>
      <div class="meta-list">
        <span>鍩轰簬鍐呯疆浜旂骇鏀姢瑙勫垯绨?/span>
        <span>杈撳嚭鍚垵鏀笌寤鸿鍊煎姣?/span>
      </div>
    </div>
    <div class="card panel-card">
      <div class="scenario-grid">
        <label>
          鍖烘
          <select id="recommend-section">${sectionOptions()}</select>
        </label>
        <label>
          鎯呮櫙鍚嶇О
          <input id="recommend-name" type="text" value="${state.scenario.scenarioName}" />
        </label>
        <label>
          鎵板姩绯绘暟
          <input id="recommend-excavation" type="number" min="0.8" max="1.6" step="0.05" value="${state.scenario.excavationIntensity}" />
        </label>
        <label>
          闄嶉洦绯绘暟
          <input id="recommend-rainfall" type="number" min="0" max="1.5" step="0.05" value="${state.scenario.rainfallFactor}" />
        </label>
      </div>
      <div class="scenario-grid" style="margin-top: 14px;">
        <label>
          瀹夊叏鎶樺噺绯绘暟
          <input id="recommend-safety" type="number" min="0.8" max="1.4" step="0.05" value="${state.scenario.safetyFactor}" />
        </label>
        <div class="scenario-actions">
          <button class="primary-button" id="recommend-btn" type="button">鐢熸垚寤鸿</button>
        </div>
      </div>
      ${
        latestRecommendation
          ? `
            <div class="callout">${latestRecommendation.summary}</div>
            <div class="comparison-grid">
              <div class="card">
                <h3>鏉愭枡鍙傛暟</h3>
                ${metricRow("鍠锋贩鍘氬害", latestRecommendation.materialPlan.shotcreteThicknessCm, " cm")}
                ${metricRow("閿氭潌闀垮害", latestRecommendation.materialPlan.boltLengthM, " m")}
                ${metricRow("閿氭潌闂磋窛", latestRecommendation.materialPlan.boltSpacing)}
                ${metricRow("鎷辨灦闂磋窛", latestRecommendation.materialPlan.steelArchSpacing)}
                ${metricRow("棰勭暀鍙樺舰閲?, latestRecommendation.materialPlan.reservedDeformationMm, " mm")}
              </div>
              <div class="card">
                <h3>澶嶆牳瀵规瘮</h3>
                ${metricRow("鍘熷柗娣峰帤搴?, latestRecommendation.comparison.initialShotcreteThicknessCm, " cm")}
                ${metricRow("寤鸿鍠锋贩鍘氬害", latestRecommendation.comparison.suggestedShotcreteThicknessCm, " cm")}
                ${metricRow("鍘熼敋鏉嗛暱搴?, latestRecommendation.comparison.initialBoltLengthM, " m")}
                ${metricRow("寤鸿閿氭潌闀垮害", latestRecommendation.comparison.suggestedBoltLengthM, " m")}
                ${metricRow("鎺柦鍓嶉闄╁垎", formatNumber(latestRecommendation.comparison.riskScoreBefore))}
                ${metricRow("鎺柦鍚庨浼板垎", formatNumber(latestRecommendation.comparison.riskScoreAfterMeasure))}
              </div>
            </div>
            <div class="comparison-grid" style="margin-top: 16px;">
              <div class="card">
                <h3>璁捐渚濇嵁</h3>
                <ul class="bullet-list">${latestRecommendation.decisionBasis.map((item) => `<li>${item}</li>`).join("")}</ul>
              </div>
              <div class="card">
                <h3>鎵ц鎺柦</h3>
                <ul class="bullet-list">${latestRecommendation.measures.map((item) => `<li>${item}</li>`).join("")}</ul>
              </div>
            </div>
          `
          : `<div class="empty-state">灏氭湭鐢熸垚鏀姢寤鸿銆?/div>`
      }
    </div>
  `;
}

function renderAlerts() {
  return `
    <div class="view-header">
      <div>
        <h2>棰勮澶勭疆</h2>
        <p>鎶婅Е鍙戞潯浠躲€佽矗浠讳汉鍜岀幇鍦哄姩浣滃啓鎴愬崱鐗囷紝涓嶈棰勮鍋滅暀鍦ㄨ〃鏍奸噷銆?/p>
      </div>
      <div class="meta-list">
        <span>鑷姩鎸夐闄╁垎鍊掓帓</span>
        <span>涓庢敮鎶ゅ鏍稿叡浜悓涓€濂楀尯娈典富鏁版嵁</span>
      </div>
    </div>
    <div class="alert-grid">
      ${state.alerts
        .map(
          (alert) => `
            <article class="card alert-card ${riskClass(alert.riskLevel)}">
              <h3>${alert.sectionName}</h3>
              <p>${riskPill(alert.riskLevel, alert.riskScore)}</p>
              <p><strong>瑙﹀彂鏉′欢锛?/strong>${alert.trigger}</p>
              <p><strong>澶勭疆鍔ㄤ綔锛?/strong>${alert.action}</p>
              <p><strong>璐ｄ换浜猴細</strong>${alert.owner}</p>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderReports() {
  const latestPrediction = state.predictions[0];
  const latestRecommendation = state.recommendations[0];
  const exampleCommand = `python -X utf8 pipeline_guard.py --project-dir "闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠? --requirement-name "闅ч亾鍥村博鍙樺舰棰勬祴涓庢敮鎶よ璁¤緟鍔╄蒋浠?`;
  return `
    <div class="view-header">
      <div>
        <h2>浜や粯鏍℃牳</h2>
        <p>鎶?PRD銆佺郴缁熴€乻lop 瀹℃煡鍜岃蒋钁楁潗鏂欑殑鐘舵€佹斁鍦ㄥ悓涓€椤碉紝渚夸簬鎵ц鑷姩鍖栧墠鐨勪汉宸ュ鏍搞€?/p>
      </div>
      <div class="meta-list">
        <span>鏈€缁堜互 pipeline_guard 鍒ゅ畾涓哄噯</span>
        <span>姝ら〉鐢ㄤ簬鎵ц鍓嶈嚜妫€</span>
      </div>
    </div>
    <div class="report-grid">
      <article class="card report-card">
        <h3>褰撳墠杩愯鎬?/h3>
        ${metricRow("鐧诲綍韬唤", state.user ? state.user.name : "鏈櫥褰?)}
        ${metricRow("鍙闂〉闈?, state.user ? state.user.permissions.join(" / ") : "鏃?)}
        ${metricRow("鏈€杩戦娴?, latestPrediction ? latestPrediction.sectionName : "鏆傛棤")}
        ${metricRow("鏈€杩戞敮鎶ゅ缓璁?, latestRecommendation ? latestRecommendation.sectionName : "鏆傛棤")}
        <div class="badge-row">
          <span class="badge">PRD 鐢熸垚鍚庢墽琛岄樁娈?1</span>
          <span class="badge">娴嬭瘯閫氳繃鍚庢墽琛岄樁娈?2</span>
          <span class="badge">瀹℃煡鍐欏叆 checklog 鍚庢墽琛岄樁娈?3</span>
        </div>
      </article>
      <article class="card report-card">
        <h3>鍛戒护绀轰緥</h3>
        <pre class="code-block">${exampleCommand}</pre>
        <p>鍏叡鑴氭湰璐熻矗鏈€鍚庣殑涓茶楠屾敹锛涢」鐩骇鑴氭湰璐熻矗 PRD 瀹℃牳銆佽嚜鍔ㄥ寲娴嬭瘯銆乻lop 瀹℃煡涓庢潗鏂欐墦鍖呫€?/p>
      </article>
    </div>
    <div class="card panel-card" style="margin-top: 18px;">
      <h3>鎺ュ彛涓庤鍒欐憳瑕?/h3>
      ${
        state.contracts
          ? `
            <div class="comparison-grid">
              <div class="card">
                <h3>鎺ュ彛娓呭崟</h3>
                <ul class="bullet-list">
                  ${state.contracts.api.endpoints.map((item) => `<li>${item.method} ${item.path}锛?{item.summary}</li>`).join("")}
                </ul>
              </div>
              <div class="card">
                <h3>鏀姢瑙勫垯绨?/h3>
                <ul class="bullet-list">
                  ${state.contracts.rulebook.levels.map((item) => `<li>${item.level} 绾э細鍠锋贩 ${item.shotcreteThickness} cm锛岄敋鏉?${item.boltLength} m锛屾嫳鏋?${item.steelArchSpacing}</li>`).join("")}
                </ul>
              </div>
            </div>
          `
          : `<div class="empty-state">鎺ュ彛濂戠害灏氭湭鍔犺浇銆?/div>`
      }
    </div>
  `;
}

const renderers = {
  dashboard: renderDashboard,
  sections: renderSections,
  analysis: renderAnalysis,
  designs: renderDesigns,
  alarms: renderAlerts,
  reports: renderReports,
};

function bindSectionEvents() {
  document.querySelector("#filter-btn")?.addEventListener("click", async () => {
    state.filters.keyword = document.querySelector("#keyword-input").value.trim();
    state.filters.risk = document.querySelector("#risk-select").value;
    await loadSections();
    render();
  });
  document.querySelectorAll(".section-row").forEach((row) => {
    row.addEventListener("click", async () => {
      const sectionId = row.dataset.sectionId;
      await selectSection(sectionId);
      window.location.hash = "sections";
    });
  });
}

function bindAnalysisEvents() {
  document.querySelector("#scenario-section")?.addEventListener("change", (event) => {
    state.scenario.sectionId = event.target.value;
  });
  document.querySelector("#scenario-name")?.addEventListener("input", (event) => {
    state.scenario.scenarioName = event.target.value;
  });
  document.querySelector("#scenario-excavation")?.addEventListener("input", (event) => {
    state.scenario.excavationIntensity = Number(event.target.value);
  });
  document.querySelector("#scenario-rainfall")?.addEventListener("input", (event) => {
    state.scenario.rainfallFactor = Number(event.target.value);
  });
  document.querySelector("#scenario-safety")?.addEventListener("input", (event) => {
    state.scenario.safetyFactor = Number(event.target.value);
  });
  document.querySelector("#predict-btn")?.addEventListener("click", async () => {
    await createPrediction();
    render();
  });
  document.querySelector("#load-critical-btn")?.addEventListener("click", () => {
    state.scenario = {
      sectionId: "SEC-008",
      scenarioName: "娣卞煁杞博鏆撮洦鎵板姩",
      excavationIntensity: 1.35,
      rainfallFactor: 1.1,
      safetyFactor: 1.05,
    };
    render();
  });
}

function bindDesignEvents() {
  document.querySelector("#recommend-section")?.addEventListener("change", (event) => {
    state.scenario.sectionId = event.target.value;
  });
  document.querySelector("#recommend-name")?.addEventListener("input", (event) => {
    state.scenario.scenarioName = event.target.value;
  });
  document.querySelector("#recommend-excavation")?.addEventListener("input", (event) => {
    state.scenario.excavationIntensity = Number(event.target.value);
  });
  document.querySelector("#recommend-rainfall")?.addEventListener("input", (event) => {
    state.scenario.rainfallFactor = Number(event.target.value);
  });
  document.querySelector("#recommend-safety")?.addEventListener("input", (event) => {
    state.scenario.safetyFactor = Number(event.target.value);
  });
  document.querySelector("#recommend-btn")?.addEventListener("click", async () => {
    await createRecommendation();
    render();
  });
}

function bindEventsByRoute() {
  const current = route();
  if (current === "sections") {
    bindSectionEvents();
  }
  if (current === "analysis") {
    bindAnalysisEvents();
  }
  if (current === "designs") {
    bindDesignEvents();
  }
}

function render() {
  setActiveNav();
  const current = route();
  const renderer = renderers[current] || renderDashboard;
  contentArea.innerHTML = renderer();
  bindEventsByRoute();
}

async function selectSection(sectionId) {
  const { item } = await api(`/api/sections/${sectionId}`);
  state.selectedSection = item;
  state.scenario.sectionId = item.id;
  render();
}

async function loadDashboard() {
  const { data } = await api("/api/dashboard");
  state.dashboard = data;
}

async function loadSections() {
  const query = new URLSearchParams();
  if (state.filters.keyword) {
    query.set("keyword", state.filters.keyword);
  }
  if (state.filters.risk) {
    query.set("risk", state.filters.risk);
  }
  const { items } = await api(`/api/sections${query.toString() ? `?${query.toString()}` : ""}`);
  state.sections = items;
  if (!state.selectedSection && items.length) {
    state.selectedSection = items[0];
    state.scenario.sectionId = items[0].id;
  }
}

async function loadPredictions() {
  const { items } = await api("/api/predictions");
  state.predictions = items;
}

async function loadRecommendations() {
  const { items } = await api("/api/recommendations");
  state.recommendations = items;
}

async function loadAlerts() {
  const { items } = await api("/api/alerts");
  state.alerts = items;
}

async function loadContracts() {
  const { data } = await api("/api/contracts");
  state.contracts = data;
}

async function createPrediction() {
  const { item } = await api("/api/predictions", {
    method: "POST",
    body: JSON.stringify(state.scenario),
  });
  state.predictions = [item, ...state.predictions].slice(0, 8);
}

async function createRecommendation() {
  const { item } = await api("/api/recommendations", {
    method: "POST",
    body: JSON.stringify(state.scenario),
  });
  state.recommendations = [item, ...state.recommendations].slice(0, 8);
}

async function bootstrapApp() {
  loginPanel.classList.add("hidden");
  appShell.classList.remove("hidden");
  userPill.textContent = `${state.user.name} / ${state.user.title}`;
  await Promise.all([loadDashboard(), loadSections(), loadPredictions(), loadRecommendations(), loadAlerts(), loadContracts()]);
  render();
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginMessage.textContent = "姝ｅ湪鏍￠獙韬唤...";
  const formData = new FormData(loginForm);
  try {
    const payload = Object.fromEntries(formData.entries());
    const { token, user } = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.token = token;
    state.user = user;
    localStorage.setItem("tunnel_token", token);
    loginMessage.textContent = "";
    await bootstrapApp();
  } catch (error) {
    loginMessage.textContent = error.message;
  }
});

logoutBtn.addEventListener("click", async () => {
  if (state.token) {
    try {
      await api("/api/auth/logout", { method: "POST", body: "{}" });
    } catch (error) {
      console.warn(error);
    }
  }
  resetSession();
});

window.addEventListener("hashchange", async () => {
  const current = route();
  if (current === "sections" && state.selectedSection) {
    await selectSection(state.selectedSection.id);
    return;
  }
  render();
});

async function resumeSession() {
  if (!state.token) {
    resetSession();
    return;
  }
  try {
    const { user } = await api("/api/session");
    state.user = user;
    await bootstrapApp();
  } catch (error) {
    resetSession();
  }
}

resumeSession();


