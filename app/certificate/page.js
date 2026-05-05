"use client";

import Image from "next/image";
import Link from "next/link";
import { course, profile } from "../data/siteData";
import { useClientState } from "../_hooks/useClientState";
import { useHydrated } from "../_hooks/useHydrated";

export default function CertificatePage() {
  const { state, isReady } = useClientState();
  const hydrated = useHydrated();
  const isCompleted = isReady && state.course.completed;

  return (
    <div className="container section">
      <div className="section-head">
        <h1 className="section-title">Certificate</h1>
        <p className="section-subtitle">Certificate preview and download.</p>
      </div>

      <div className="certificate-panel">
        <Image
          className="certificate-image"
          src="/assets/certificate.jpg"
          alt="Certificate of completion"
          width={1200}
          height={850}
          priority
          sizes="(max-width: 960px) 100vw, 960px"
          style={{ width: "100%", height: "auto" }}
        />
        <div className="hero-actions">
          <a className="btn primary" href="/assets/certificate.jpg" download>
            Download certificate
          </a>
          <Link className="btn ghost" href="/profile">
            View profile
          </Link>
        </div>
        <span className="pill">
          Issued to {profile.name} - {course.title}
        </span>
        {hydrated && !isCompleted ? (
          <div className="callout">
            Course completion status is not marked yet. You can still view and
            download the certificate for this demo.
          </div>
        ) : null}
      </div>
    </div>
  );
}
