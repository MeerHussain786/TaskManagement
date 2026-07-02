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
    <aside className="w-64 h-screen hidden md:flex flex-col border-r border-white/5 bg-background/50 backdrop-blur-xl relative z-40">
      
      {/* Brand */}
      <div className="h-20 flex items-center px-6 border-b border-white/5">
        <h1 className="text-xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary uppercase tracking-widest">
          TaskFlow
        </h1>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto custom-scrollbar">
        {links.map((link) => {
          const isActive = pathname === link.href || (link.href !== "/dashboard" && link.href !== "/" && pathname.startsWith(link.href));
          const Icon = link.icon;
          
          if (link.isMain) {
            return (
              <div key={link.href} className="pt-4 pb-2">
                <Link href={link.href}>
                  <div className="w-full h-12 bg-gradient-to-r from-primary to-secondary rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-primary/20 text-white hover:shadow-primary/40 hover:-translate-y-0.5 transition-all">
                    <Icon size={20} strokeWidth={2.5} />
                    <span className="font-semibold text-sm tracking-wide">{link.label}</span>
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
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 relative z-10",
                isActive ? "text-white" : "text-muted-foreground hover:text-white hover:bg-white/5"
              )}>
                <Icon size={20} className={cn(isActive && "drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]")} />
                <span className="text-sm font-medium tracking-wide">{link.label}</span>
              </div>
              
              {isActive && (
                <motion.div
                  layoutId="sidebar-indicator"
                  className="absolute inset-0 bg-white/10 rounded-xl z-0 border border-white/10"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
            </Link>
          );
        })}
      </nav>
      
      {/* User profile brief */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-secondary p-0.5">
             <div className="w-full h-full bg-background rounded-full flex items-center justify-center">
                <User size={16} className="text-muted-foreground" />
             </div>
          </div>
          <div>
            <p className="text-sm font-medium text-white">
              {mounted && user ? (user.full_name || user.username) : 'Loading...'}
            </p>
            <p className="text-xs text-muted-foreground truncate max-w-[120px]">
              {mounted && user ? user.email : '...'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
