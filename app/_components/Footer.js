import { site } from "../data/siteData";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <div className="footer-title">{site.name}</div>
          {site.tagline ? <p>{site.tagline}</p> : null}
        </div>
        <div>
          <div className="footer-title">Programs</div>
          <p>BI Dashboards</p>
          <p>Data Storytelling</p>
          <p>Analytics Foundations</p>
        </div>
        <div>
          <div className="footer-title">Support</div>
          <p>Help center</p>
          <p>Certificate verification</p>
          <p>Learning roadmap</p>
        </div>
        <div>
          <div className="footer-title">Community</div>
          <p>Mentor sessions</p>
          <p>Capstone reviews</p>
          <p>Alumni network</p>
        </div>
      </div>
    </footer>
  );
}
