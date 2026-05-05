"use client";

import Image from "next/image";
import Link from "next/link";
import { site, profile } from "../data/siteData";
import { useClientState } from "../_hooks/useClientState";
import { useHydrated } from "../_hooks/useHydrated";
import { applyLogout } from "../lib/clientState";

export default function Header() {
  const { state, updateState, isReady } = useClientState();
  const hydrated = useHydrated();
  const isLoggedIn = isReady && state.isLoggedIn;
  const logoSrc = "/assets/great-learning-logo.svg";

  const handleLogout = () => {
    updateState((prev) => applyLogout(prev));
  };

  return (
    <header className="site-header">
      
      <div className="container nav-bar">
        <div className="brand">
          <Link className="brand-link" href="/">
            <Image
              className="brand-logo"
              src={logoSrc}
              alt="Great Learning logo"
              width={180}
              height={48}
              priority
            />
            <div className="brand-text">
              
              {site.tagline ? (
                <span className="brand-subtitle">{site.tagline}</span>
              ) : null}
            </div>
          </Link>
        </div>
        <nav className="nav-links">
          <Link className="nav-link" href="/">
            Home
          </Link>
          <Link className="nav-link" href="/courses">
            Courses
          </Link>
          <Link className="nav-link" href="/my-learning">
            My Learning
          </Link>
          <Link className="nav-link" href="/certificate">
            Certificate
          </Link>
        </nav>
        <div className="nav-actions">
          <Link className="btn ghost" href="/profile">
            {profile.name}
          </Link>
          {hydrated && isLoggedIn && (
            <button className="btn ghost" onClick={handleLogout} type="button">
              Sign out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
