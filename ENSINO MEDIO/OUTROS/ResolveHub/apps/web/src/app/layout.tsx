import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000"),
  title: "ResolveHub — Central inteligente de suporte",
  description: "Pesquise procedimentos e gere respostas fundamentadas para atendimentos Small Commerce e ZWeb.",
  openGraph: {
    title: "ResolveHub",
    description: "Central inteligente de suporte",
    images: [{ url: "/og.png", width: 1728, height: 910, alt: "ResolveHub — Central inteligente de suporte" }],
    locale: "pt_BR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ResolveHub",
    description: "Central inteligente de suporte",
    images: ["/og.png"],
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
