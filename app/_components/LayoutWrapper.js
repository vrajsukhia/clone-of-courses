"use client";

import { usePathname } from "next/navigation";

export default function LayoutWrapper({ children }) {
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  // Hide footer on home page only
  if (isHomePage) {
    return null;
  }

  return children;
}
