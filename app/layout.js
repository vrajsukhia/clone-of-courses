import "./globals.css";
import Header from "./_components/Header";
import Footer from "./_components/Footer";
import LayoutWrapper from "./_components/LayoutWrapper";

export const metadata = {
  title: "Free Online Course & Certificate to Learn & Build Skills",
  description:
    "Free online learning with course catalog, progress tracking, and certificate download.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <div className="page-shell">
          <Header />
          <main className="page-main">{children}</main>
          <LayoutWrapper>
            <Footer />
          </LayoutWrapper>
        </div>
      </body>
    </html>
  );
}
