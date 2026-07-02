"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Calendar, PlusCircle, BarChart2, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

export function BottomNav() {
  const pathname = usePathname();

  const links = [
    { href: "/dashboard", label: "Home", icon: Home },
    { href: "/calendar", label: "Calendar", icon: Calendar },
    { href: "/add", label: "Add", icon: PlusCircle, isMain: true },
    { href: "/analytics", label: "Analytics", icon: BarChart2 },
    { href: "/profile", label: "Profile", icon: User },
  ];

  return (
    <div className="fixed bottom-0 w-full max-w-md mx-auto left-0 right-0 z-50">
      <div className="glass-dark m-4 rounded-3xl p-2 flex justify-between items-center relative overflow-hidden">
        {links.map((link) => {
          const isActive = pathname === link.href;
          const Icon = link.icon;
          
          if (link.isMain) {
            return (
              <Link key={link.href} href={link.href} className="relative -top-5 z-10 px-2">
                <div className="w-14 h-14 bg-gradient-to-tr from-primary to-secondary rounded-full flex items-center justify-center shadow-lg shadow-primary/30 text-white glitch-hover">
                  <Icon size={28} strokeWidth={2.5} />
                </div>
              </Link>
            )
          }

          return (
            <Link
              key={link.href}
              href={link.href}
              className="flex flex-col items-center justify-center w-14 h-14 relative"
            >
              <div className={cn(
                "flex flex-col items-center justify-center transition-all duration-200 z-10",
                isActive ? "text-white scale-110" : "text-muted-foreground hover:text-white"
              )}>
                <Icon size={22} className={cn("mb-1", isActive && "drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]")} />
                <span className="text-[10px] font-medium tracking-wide">{link.label}</span>
              </div>
              
              {isActive && (
                <motion.div
                  layoutId="bottom-nav-indicator"
                  className="absolute inset-0 bg-white/10 rounded-2xl z-0"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
