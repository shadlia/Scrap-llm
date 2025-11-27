"use client";

import Image from "next/image";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function Logo() {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // After mounting, we have access to the theme
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="relative w-[180px] h-[60px]">
        <Image
          src="/Choose_Logo_Black.png"
          alt="Choose Logo"
          fill
          className="object-contain"
          priority
        />
      </div>
    );
  }

  return (
    <div className="relative w-[180px] h-[60px]">
      <Image
        src={
          theme === "dark" ? "/Choose_Logo_Black.png" : "/Choose_Logo_White.svg"
        }
        alt="Choose Logo"
        fill
        className="object-contain"
        priority
      />
    </div>
  );
}
