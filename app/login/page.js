"use client";

import Link from "next/link";
import { profile } from "../data/siteData";
import { useClientState } from "../_hooks/useClientState";
import { applyLogin, applyLogout } from "../lib/clientState";

export default function LoginPage() {
  const { state, updateState, isReady } = useClientState();
  const isLoggedIn = isReady && state.isLoggedIn;

  const handleLogin = () => {
    updateState((prev) => applyLogin(prev));
  };

  const handleLogout = () => {
    updateState((prev) => applyLogout(prev));
  };

  return (
    <div className="container section">
      <div className="section-head">
        <h1 className="section-title">Learner Sign In</h1>
        <p className="section-subtitle">
          This demo already has a registered account for {profile.name}.
        </p>
      </div>

      <div className="info-card">
        <h3>Account</h3>
        <p className="section-subtitle">Name: {profile.name}</p>
        <p className="section-subtitle">Email: {profile.email}</p>
        {isLoggedIn ? (
          <div className="callout">You are signed in as {profile.name}.</div>
        ) : null}
        <div className="hero-actions">
          {!isLoggedIn ? (
            <button className="btn primary" type="button" onClick={handleLogin}>
              Continue as {profile.name}
            </button>
          ) : (
            <button className="btn ghost" type="button" onClick={handleLogout}>
              Sign out
            </button>
          )}
          <Link className="btn outline" href="/my-learning">
            Go to My Learning
          </Link>
          <Link className="btn ghost" href="/profile">
            View profile
          </Link>
        </div>
      </div>
    </div>
  );
}
