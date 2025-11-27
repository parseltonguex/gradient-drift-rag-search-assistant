// ===============================
// auth.js (PKCE + Cognito + UI wiring)
// ===============================

// ---- CONFIG ----
const CF_ROOT = "https://d1pfw1640errhz.cloudfront.net";
const COGNITO_DOMAIN = "https://eu-west-2yjbtfgb5q.auth.eu-west-2.amazoncognito.com";
const CLIENT_ID = "5hh9g0pqhog16bkangcp4p26o2";
const REDIRECT_URI = `${CF_ROOT}/auth/callback.html`;
const SCOPES = ["openid", "profile", "email"];

// If you ever want to use auth.askApi later, keep this:
const API_BASE = `${CF_ROOT}/api`;

// ---- STORAGE KEYS ----
const SK = {
  ID_TOKEN: "id_token",
  ACCESS_TOKEN: "access_token",
  PKCE_CV: "pkce_cv",
};

// ---- HELPERS ----
function b64urlFromBytes(bytes) {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function sha256Base64Url(input) {
  const enc = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest("SHA-256", enc);
  return b64urlFromBytes(new Uint8Array(digest));
}

function setTokens({ id_token, access_token }) {
  if (id_token) sessionStorage.setItem(SK.ID_TOKEN, id_token);
  if (access_token) sessionStorage.setItem(SK.ACCESS_TOKEN, access_token);
}

function clearTokens() {
  sessionStorage.removeItem(SK.ID_TOKEN);
  sessionStorage.removeItem(SK.ACCESS_TOKEN);
}

function getAccessToken() {
  return sessionStorage.getItem(SK.ACCESS_TOKEN) || null;
}

function getIdToken() {
  return sessionStorage.getItem(SK.ID_TOKEN) || null;
}

function parseJwt(token) {
  try {
    const [, payload] = token.split(".");
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function isSignedIn() {
  const at = getAccessToken();
  if (!at) return false;
  const claims = parseJwt(at);
  return !!(claims && claims.exp && claims.exp > Math.floor(Date.now() / 1000));
}

// ---- UI BINDINGS ----
// (updated to match your current HTML IDs)
function updateUI() {
  const userEl = document.getElementById("user-email");     // span in your header
  const overlay = document.getElementById("auth-overlay");  // full-screen overlay
  const askBtn = document.getElementById("askBtn");         // Ask button
  const queryInput = document.getElementById("query");      // textarea

  const authed = isSignedIn();

  if (userEl) {
    if (authed) {
      const idt = getIdToken();
      const claims = idt ? parseJwt(idt) : null;
      const name =
        (claims && (claims.name || claims["cognito:username"] || claims.email)) ||
        "Signed in";
      userEl.textContent = name;
      userEl.classList.remove("hidden");
    } else {
      userEl.textContent = "";
      userEl.classList.add("hidden");
    }
  }

  const disableInputs = !authed;
  if (askBtn) askBtn.disabled = disableInputs;
  if (queryInput) queryInput.disabled = disableInputs;
  if (overlay) overlay.classList.toggle("hidden", authed);
}

// ---- COOKIE UTILS ----
function setCookie(name, value, seconds) {
  const maxAge = seconds ? `; Max-Age=${Math.floor(seconds)}` : "";
  document.cookie = `${name}=${encodeURIComponent(
    value
  )}; Path=/; SameSite=Lax; Secure${maxAge}`;
}

function clearCookie(name) {
  document.cookie = `${name}=; Path=/; Max-Age=0; SameSite=Lax; Secure`;
}

// ---- AUTH FLOWS ----
async function startLogin() {
  // 1) Generate code_verifier + challenge
  const rv = crypto.getRandomValues(new Uint8Array(32));
  const codeVerifier = b64urlFromBytes(rv);
  const codeChallenge = await sha256Base64Url(codeVerifier);

  // 2) Persist verifier
  localStorage.setItem(SK.PKCE_CV, codeVerifier);
  sessionStorage.setItem(SK.PKCE_CV, codeVerifier);
  setCookie("pkce_cv", codeVerifier, 300); // 5 mins

  // 3) Create state object
  const stateObj = { cv: codeVerifier, ts: Date.now() };
  const state = btoa(JSON.stringify(stateObj))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

  // 4) Build authorize URL
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    response_type: "code",
    redirect_uri: REDIRECT_URI,
    scope: SCOPES.join(" "),
    code_challenge_method: "S256",
    code_challenge: codeChallenge,
    state,
  });
  const authorizeUrl = `${COGNITO_DOMAIN}/oauth2/authorize?${params.toString()}`;

  // 5) Redirect
  window.location.href = authorizeUrl;
}

function startLogout() {
  clearTokens();
  updateUI();
  clearCookie("pkce_cv");

  const p = new URLSearchParams({
    client_id: CLIENT_ID,
    logout_uri: CF_ROOT + "/",
  });
  window.location.href = `${COGNITO_DOMAIN}/logout?${p.toString()}`;
}

// ---- PROTECTED FETCH ----
async function authFetch(input, init = {}) {
  const token = getAccessToken();
  if (!token) throw new Error("Not authenticated");
  const headers = new Headers(init.headers || {});
  headers.set("Authorization", `Bearer ${token}`);
  headers.set("Content-Type", headers.get("Content-Type") || "application/json");
  return fetch(input, { ...init, headers });
}

async function askApi(payload) {
  const res = await authFetch(`${API_BASE}/ask`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${txt || res.statusText}`);
  }
  return res.json();
}

// ---- ORIGIN GUARD ----
(function originGuard() {
  try {
    const allowed = new URL(CF_ROOT).host;
    if (location.host !== allowed) {
      console.warn(`Redirecting to canonical origin: ${allowed}`);
      window.location.replace(
        `${CF_ROOT}${location.pathname}${location.search}${location.hash}`
      );
    }
  } catch {
    // ignore
  }
})();

// ---- BOOT ----
window.addEventListener("DOMContentLoaded", () => {
  const signInBtn = document.getElementById("sign-in-btn");
  const signOutBtn = document.getElementById("sign-out-btn");

  if (signInBtn) {
    signInBtn.addEventListener("click", () => {
      startLogin();
    });
  }

  if (signOutBtn) {
    signOutBtn.addEventListener("click", () => {
      startLogout();
    });
  }

  // Just update UI based on existing tokens.
  // (No auto-redirect here — user clicks "Sign In".)
  updateUI();

  // Expose minimal API for app.js
  window.auth = Object.freeze({
    isSignedIn,
    getAccessToken,
    getIdToken,
    startLogin,
    startLogout,
    fetch: authFetch,
    askApi,
    updateUI,
  });
});
