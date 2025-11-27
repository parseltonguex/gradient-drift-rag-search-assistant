// ==============================
// main-auth-v8.js
// ==============================

// ---- PKCE UTILS ----

function generateCodeVerifier(length = 64) {
  const array = new Uint32Array(length);
  window.crypto.getRandomValues(array);
  return Array.from(array, dec => ('0' + dec.toString(16)).slice(-2)).join('');
}

async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await window.crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// ---- CONFIG ----

const COGNITO_DOMAIN = "https://eu-west-2yjbtfgb5q.auth.eu-west-2.amazoncognito.com";
const CLIENT_ID = "5hh9g0pqhog16bkangcp4p26o2";
const REDIRECT_URI = "https://d1pfw1640errhz.cloudfront.net/auth/callback.html";

// ---- EARLY AUTH GUARD ----

const idToken = localStorage.getItem("id_token");

if (!idToken && window.location.pathname !== "/auth/callback.html") {
  document.body.innerHTML = "<p style='text-align:center; padding:2rem;'>🔐 Redirecting to sign-in…</p>";
  const codeVerifier = generateCodeVerifier();
  localStorage.setItem("pkce_code_verifier", codeVerifier);

  generateCodeChallenge(codeVerifier).then(codeChallenge => {
    const loginUrl =
      `${COGNITO_DOMAIN}/oauth2/authorize?response_type=code` +
      `&client_id=${CLIENT_ID}` +
      `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
      `&code_challenge_method=S256&code_challenge=${codeChallenge}`;

    window.location.href = loginUrl;
  });

  throw new Error("Redirecting to login — unauthenticated user");
}

// ---- TOKEN UTILS ----

function isSignedIn() {
  const idToken = localStorage.getItem("id_token");
  if (!idToken) return false;
  const [, payload] = idToken.split(".");
  const decoded = JSON.parse(atob(payload));
  return Date.now() < decoded.exp * 1000;
}

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getIdToken() {
  return localStorage.getItem("id_token");
}

function startLogin() {
  const codeVerifier = generateCodeVerifier();
  localStorage.setItem("pkce_code_verifier", codeVerifier);

  generateCodeChallenge(codeVerifier).then((codeChallenge) => {
    const loginUrl =
      `${COGNITO_DOMAIN}/oauth2/authorize?response_type=code` +
      `&client_id=${CLIENT_ID}` +
      `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
      `&code_challenge_method=S256&code_challenge=${codeChallenge}`;
    window.location.href = loginUrl;
  });
}

function startLogout() {
  localStorage.clear();
  window.location.reload();
}

async function authFetch(url, options = {}) {
  const token = getAccessToken();
  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });
}

// ---- RAG CALL ----

async function askApi(input, model, topk) {
  const res = await authFetch("/api/ask", {
    method: "POST",
    body: JSON.stringify({
      query: input,
      model: model,
      k: topk         // ✅ NOT topk: topk
    }),
    headers: {
      "Content-Type": "application/json",
    },
  });

  const json = await res.json();
  console.log("📦 askApi response:", json);
  return json;
}

// ---- UI UPDATE ----

function updateUI() {
  console.log("🔄 Running updateUI");
  const overlay = document.getElementById("auth-overlay");
  const signInBtn = document.getElementById("sign-in-btn");
  const signOutBtn = document.getElementById("sign-out-btn");

  if (isSignedIn()) {
    if (overlay) overlay.style.display = "none";
    if (signInBtn) signInBtn.style.display = "none";
    if (signOutBtn) signOutBtn.style.display = "inline-block";
  } else {
    if (overlay) overlay.style.display = "flex";
    if (signInBtn) signInBtn.style.display = "inline-block";
    if (signOutBtn) signOutBtn.style.display = "none";
  }
}

// ---- BOOTSTRAP ----

window.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM loaded");

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

  const signInBtn = document.getElementById("sign-in-btn");
  const signOutBtn = document.getElementById("sign-out-btn");

  if (signInBtn) signInBtn.addEventListener("click", () => startLogin());
  if (signOutBtn) signOutBtn.addEventListener("click", () => startLogout());

  if (localStorage.getItem("just_signed_in") === "1") {
    console.log("🟢 Just signed in — forcing UI update");
    updateUI();
    localStorage.removeItem("just_signed_in");
    return;
  }

  if (isSignedIn()) {
    console.log("✅ Signed in — updating UI");
    updateUI();
  } else {
    console.log("🔒 Not signed in — UI remains gated");
  }
});
