"use client";

import Link from "next/link";
import { course } from "../../data/siteData";
import { useClientState } from "../../_hooks/useClientState";
import { useHydrated } from "../../_hooks/useHydrated";
import { applyCourseCompletion } from "../../lib/clientState";

export default function CourseDetail() {
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
        <span className="pill">Power BI Track</span>
        <h1 className="section-title">{course.title}</h1>
        <p className="section-subtitle">{course.summary}</p>
      </div>

      <div className="two-column">
        <div className="info-card">
          <h3>Course overview</h3>
          <div className="course-meta">
            <span>Level: {course.level}</span>
            <span>Duration: {course.duration}</span>
            <span>{course.lessons} lessons</span>
            <span>Rating: {course.rating}</span>
          </div>
          {hydrated && (
            <>
              <div>
                <div className="section-subtitle">Progress</div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
              </div>
              <div className="hero-actions">
                <button className="btn primary" type="button" onClick={handleComplete}>
                  {isCompleted ? "Course completed" : "Mark course complete"}
                </button>
                <Link className="btn ghost" href="/my-learning">
                  View my learning
                </Link>
              </div>
              <span className="pill">{course.certificate}</span>
              {!state.isLoggedIn && (
                <div className="callout">
                  Sign in to keep your progress and unlock the certificate download.
                </div>
              )}
            </>
          )}
        </div>

        <div className="info-card">
          <h3>What you will build</h3>
          <ul className="list">
            {course.outcomes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <div className="chip-row">
            {course.skills.map((skill) => (
              <span key={skill} className="chip">
                {skill}
              </span>
            ))}
          </div>
          {hydrated && (
            <>
              {isCompleted ? (
                <Link className="btn outline" href="/certificate">
                  Download certificate
                </Link>
              ) : (
                <span className="pill">Complete the course to unlock</span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <h2 className="section-title">Full syllabus</h2>
          <p className="section-subtitle">
            A complete breakdown of every module and lesson inside the course.
          </p>
        </div>
        <div className="card-grid">
          {course.modules.map((module) => (
            <div key={module.title} className="info-card">
              <h3>{module.title}</h3>
              <ul className="list">
                {module.lessons.map((lesson) => (
                  <li key={lesson.title}>
                    {lesson.title} <span className="section-subtitle">({lesson.length})</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
