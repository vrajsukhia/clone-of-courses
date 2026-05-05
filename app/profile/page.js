"use client";

import Link from "next/link";
import { course, profile } from "../data/siteData";
import { useClientState } from "../_hooks/useClientState";
import { useHydrated } from "../_hooks/useHydrated";

export default function ProfilePage() {
  const { state, isReady } = useClientState();
  const hydrated = useHydrated();
  const isLoggedIn = isReady && state.isLoggedIn;

  return (
    <div className="container section">
      <div className="section-head">
        <h1 className="section-title">Profile</h1>
        <p className="section-subtitle">
          View learner details, badges, and current course progress.
        </p>
      </div>

      {hydrated && !isLoggedIn ? (
        <div className="callout">
          You are viewing the demo profile. Sign in to keep progress synced.
        </div>
      ) : null}

      <div className="info-card profile-card">
        <div className="avatar">AS</div>
        <div>
          <h3>{profile.name}</h3>
          <p className="section-subtitle">{profile.title}</p>
          <div className="course-meta">
            <span>{profile.location}</span>
            <div>
            <span>Member since {profile.memberSince}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="info-card">
          <h3>About</h3>
          <p className="section-subtitle">{profile.bio}</p>
        </div>
        <div className="info-card">
          <h3>Contact</h3>
          <ul className="list">
            <li>Email: {profile.email}</li>
            <li>Phone: +91 75670 87542</li>
            <li>Location: {profile.location}</li>
          </ul>
        </div>
       
        <div className="info-card">
          <h3>Focus areas</h3>
          <ul className="list">
            {profile.skills.map((skill) => (
              <li key={skill}>{skill}</li>
            ))}
          </ul>
        </div>
        {hydrated && (
          <div className="info-card">
            <h3>Learning status</h3>
            <ul className="list">
              <li>Current course: {course.title}</li>
              <li>Progress: {state.course.progress}%</li>
              <li>Last lesson: {state.course.lastLesson}</li>
              <li>Certificate status: {state.course.completed ? "Ready" : "Locked"}</li>
            </ul>
            <Link className="btn outline" href="/certificate">
              View certificate
            </Link>
          </div>
        )}
        <div className="info-card">
          <h3>Certificates</h3>
          <ul className="list">
            {profile.certificates.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
