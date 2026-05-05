"use client";

import Link from "next/link";
import { course, profile } from "../data/siteData";
import { useClientState } from "../_hooks/useClientState";
import { useHydrated } from "../_hooks/useHydrated";
import { applyCourseCompletion } from "../lib/clientState";

export default function MyLearning() {
  const { state, updateState, isReady } = useClientState();
  const hydrated = useHydrated();
  const isCompleted = isReady && state.course.completed;
  const progress = isReady ? state.course.progress : 62;

  const handleComplete = () => {
    updateState((prev) => applyCourseCompletion(prev));
  };

  return (
    <div className="container section">
      <div className="section-head">
        <h1 className="section-title">My Learning</h1>
        <p className="section-subtitle">
          Track progress, resume lessons, and unlock your certificate.
        </p>
      </div>

      {hydrated && !state.isLoggedIn && (
        <div className="info-card">
          <h3>Sign in to save your progress</h3>
          <p className="section-subtitle">
            Use your learner profile to keep progress synced across sessions.
          </p>
          <Link className="btn primary" href="/login">
            Continue as {profile.name}
          </Link>
        </div>
      )}

      {hydrated && (
        <div className="info-card">
          <div className="profile-card">
            <div className="avatar">AS</div>
            <div>
              <h3>{course.title}</h3>
              <p className="section-subtitle">Last lesson: {state.course.lastLesson}</p>
              <div className="course-meta">
                <span>Progress: {progress}%</span>
                <span>{course.duration}</span>
                <span>{course.lessons} lessons</span>
              </div>
            </div>
          </div>
          <div className="progress-track" style={{ marginTop: "14px" }}>
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="hero-actions" style={{ marginTop: "18px" }}>
            <Link className="btn primary" href={`/courses/${course.slug}`}>
              Resume course
            </Link>
            <button className="btn ghost" type="button" onClick={handleComplete}>
              {isCompleted ? "Course completed" : "Mark course complete"}
            </button>
            <Link className="btn outline" href="/certificate">
              View certificate
            </Link>
          </div>
          {isCompleted && (
            <span className="pill">Completed on {state.course.completedOn}</span>
          )}
        </div>
      )}
    </div>
  );
}
