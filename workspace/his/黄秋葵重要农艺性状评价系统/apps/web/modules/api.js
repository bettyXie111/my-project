const base = "";

async function request(method, path, body) {
  const init = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) init.body = JSON.stringify(body);
  const res = await fetch(`${base}${path}`, init);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${txt}`.trim());
  }
  return await res.json();
}

export const api = {
  listVarieties: (q) => request("GET", `/api/varieties?q=${encodeURIComponent(q || "")}`),
  createVariety: (payload) => request("POST", "/api/varieties", payload),
  updateVariety: (id, payload) => request("PUT", `/api/varieties/${encodeURIComponent(id)}`, payload),

  listTraits: (q) => request("GET", `/api/traits?q=${encodeURIComponent(q || "")}`),
  createTrait: (payload) => request("POST", "/api/traits", payload),
  updateTrait: (id, payload) => request("PUT", `/api/traits/${encodeURIComponent(id)}`, payload),

  listTrials: (q) => request("GET", `/api/trials?q=${encodeURIComponent(q || "")}`),
  createTrial: (payload) => request("POST", "/api/trials", payload),
  getTrial: (id) => request("GET", `/api/trials/${encodeURIComponent(id)}`),
  addPlot: (trialId, payload) => request("POST", `/api/trials/${encodeURIComponent(trialId)}/plots`, payload),

  listObservations: (params) => {
    const qs = new URLSearchParams(params || {}).toString();
    return request("GET", `/api/observations${qs ? `?${qs}` : ""}`);
  },
  createObservation: (payload) => request("POST", "/api/observations", payload),
  setObservationStatus: (id, payload) => request("PUT", `/api/observations/${encodeURIComponent(id)}/status`, payload),

  listProfiles: (q) => request("GET", `/api/score-profiles?q=${encodeURIComponent(q || "")}`),
  createProfile: (payload) => request("POST", "/api/score-profiles", payload),
  trialScores: (trialId, profileId) =>
    request("GET", `/api/trials/${encodeURIComponent(trialId)}/scores?profile_id=${encodeURIComponent(profileId || "")}`),

  listAudit: (limit) => request("GET", `/api/audit?limit=${encodeURIComponent(limit || 200)}`),
};

