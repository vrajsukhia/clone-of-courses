"use client";

import { usePathname } from "next/navigation";
import Header from "./Header";

export default function ConditionalHeader() {
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  // Don't show header on home page (iframe has its own navbar)
  if (isHomePage) {
    return null;
  }

  return <Header />;
}
