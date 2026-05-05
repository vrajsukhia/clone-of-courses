import Image from "next/image";
import Link from "next/link";
import { courses } from "../data/siteData";

export default function Courses() {
  return (
    <div className="container section">
      <div className="section-head">
        <h1 className="section-title">Course Catalog</h1>
        <p className="section-subtitle">
          Explore curated learning paths focused on analytics, visualization, and
          reporting.
        </p>
      </div>

      <div className="chip-row">
        <span className="chip">Data Visualization</span>
        <span className="chip">Business Intelligence</span>
        <span className="chip">Dashboards</span>
        <span className="chip">Storytelling</span>
      </div>

      <div className="premium-course-grid">
        {courses.map((item) => (
          <div key={item.title} className="premium-course-card">
            <div className="premium-course-card__section">
              <div className="premium-course-card__img-section">
                <div className="premium-course-card__chip-container">
                  <div className={`premium-course-card__chip--${item.tier?.toLowerCase() || 'free'}`}>
                    <span>{item.tier || 'FREE'}</span>
                  </div>
                </div>
                {item.partnerLogo && (
                  <div className="premium-course-card__partner-logo-section">
                    <Image
                      className="premium-course-card__partner-logo-img"
                      src={item.partnerLogo}
                      alt={`${item.partner} logo`}
                      width={40}
                      height={40}
                    />
                  </div>
                )}
              </div>
              <div className="premium-course-card__content-section">
                <div className="premium-course-card__rating-learner-section">
                  <span className="new_course_dot">
                    {item.projects} {item.projects === 1 ? 'project' : 'projects'}
                  </span>
                </div>

                <div className="premium-course-card__heading-section">
                  {item.slug ? (
                    <Link href={`/courses/${item.slug}`} className="premium-course-card__title">
                      {item.title}
                    </Link>
                  ) : (
                    <h3 className="premium-course-card__title">{item.title}</h3>
                  )}
                </div>

                <div className="premium-course-card__duration-section">
                  <span>{item.videoContent}</span>
                </div>

                <div className="premium-course-card__footer-section">
                  {item.slug ? (
                    <Link className="btn premium-card-btn" href={`/courses/${item.slug}`}>
                      View Course
                    </Link>
                  ) : (
                    <span className="pill">Coming soon</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

