"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Calendar, PlusCircle, BarChart2, User, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useAuthStore } from "@/store/useAuthStore";

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: Home },
    { href: "/calendar", label: "Calendar", icon: Calendar },
    { href: "/tasks", label: "Board", icon: LayoutDashboard },
    { href: "/add", label: "Add Task", icon: PlusCircle, isMain: true },
    { href: "/analytics", label: "Analytics", icon: BarChart2 },
    { href: "/profile", label: "Profile", icon: User },
  ];

  return (
    <aside className="w-64 h-screen hidden md:flex flex-col bg-black/20 backdrop-blur-xl border-r border-white/10 relative z-40">
      
      {/* Brand */}
      <div className="h-20 flex items-center px-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">
          TaskFlow
        </h1>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        {links.map((link) => {
          const isActive = pathname === link.href || (link.href !== "/dashboard" && link.href !== "/" && pathname.startsWith(link.href));
          const Icon = link.icon;
          
          if (link.isMain) {
            return (
              <div key={link.href} className="pt-4 pb-2">
                <Link href={link.href}>
                  <div className="w-full h-12 bg-primary rounded-full flex items-center justify-center gap-2 text-white font-bold hover:scale-105 transition-transform hover:opacity-90 shadow-lg shadow-primary/25">
                    <Icon size={20} strokeWidth={2.5} />
                    <span className="text-sm tracking-wide">{link.label}</span>
                  </div>
                </Link>
              </div>
            )
          }

          return (
            <Link
              key={link.href}
              href={link.href}
              className="block relative"
            >
              <div className={cn(
                "flex items-center gap-4 px-4 py-3 rounded-md transition-all duration-200 relative z-10",
                isActive ? "text-white bg-white/10 shadow-inner" : "text-white/60 hover:text-white hover:bg-white/5"
              )}>
                <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
                <span className={cn("text-sm tracking-wide", isActive ? "font-bold" : "font-medium")}>{link.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>
      
      {/* User profile brief */}
      <div className="p-4 mt-auto mb-4">
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full bg-white/10 border border-white/20 flex items-center justify-center shadow-inner">
            <User size={20} className="text-white/70" />
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-bold text-white truncate">
              {mounted && user ? (user.full_name || user.username) : 'Loading...'}
            </p>
            <p className="text-xs text-white/50 truncate max-w-[120px]">
              {mounted && user ? user.email : '...'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
