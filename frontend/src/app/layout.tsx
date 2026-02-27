import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { CommandPalette } from "@/components/layout/command-palette";
import "./globals.css";

export const metadata: Metadata = {
  title: "MetaMemory Studio",
  description: "Memory control plane for agentic systems",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <CommandPalette />
          {children}
        </Providers>
      </body>
    </html>
  );
}
