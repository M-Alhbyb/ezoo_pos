import type { Metadata } from "metadata";

export const metadata: Metadata = {
  title: "EZOO POS",
  description: "Point of Sale System for Solar Panel Business",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.NodeNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}