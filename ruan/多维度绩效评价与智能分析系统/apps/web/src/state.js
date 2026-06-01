const STORAGE_KEY = "performance-platform-session";

const initialState = {
  token: null,
  refreshToken: null,
  user: null,
  permissions: [],
  route: "dashboard",
  flash: null,
};

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { ...initialState };
    }
    return { ...initialState, ...JSON.parse(raw) };
  } catch (error) {
    return { ...initialState };
  }
}

export const state = loadState();

export function persistState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function setSession(payload) {
  state.token = payload.accessToken;
  state.refreshToken = payload.refreshToken;
  state.user = payload.user;
  persistState();
}

export function clearSession() {
  state.token = null;
  state.refreshToken = null;
  state.user = null;
  state.permissions = [];
  persistState();
}

export function setUserContext(payload) {
  state.user = payload.user;
  state.permissions = payload.permissions || [];
  persistState();
}

export function setFlash(type, text) {
  state.flash = { type, text, timestamp: Date.now() };
}
