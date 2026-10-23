import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FORGE",
  description: "Framework for Orchestrated Report Generation and Evaluation",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>
        <header className="forge-banner">
          <strong>FORGE</strong>
          <span>Framework for Orchestrated Report Generation and Evaluation</span>
          <nav>
            <a href="/">Demandes</a>
            <a href="/governance">Gouvernance</a>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
