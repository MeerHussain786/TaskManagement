"use client"

import { LogOut, Moon, Bell, Shield, User as UserIcon, Settings, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/useAuthStore";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function ProfileView() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const isDark = theme === "dark" || theme === "system"; // We forced everything to dark anyway, but this is the real toggle

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 max-w-4xl mx-auto min-h-screen">
      
      {/* Profile Header */}
      <div className="glass p-10 rounded-3xl flex flex-col md:flex-row items-center gap-8 bg-gradient-to-r from-background to-background/50 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        
        <div className="relative shrink-0">
          <div className="w-32 h-32 rounded-full bg-gradient-to-tr from-primary to-secondary p-1">
            <div className="w-full h-full bg-background rounded-full flex items-center justify-center border-4 border-background">
              <UserIcon className="w-12 h-12 text-muted-foreground" />
            </div>
          </div>
        </div>
        
        <div className="text-center md:text-left flex-1">
          <h1 className="text-4xl font-bold text-white mb-2">{mounted ? (user?.full_name || user?.username || 'Guest') : 'Loading User...'}</h1>
          <p className="text-muted-foreground text-lg mb-6">{mounted ? (user?.email || 'No email provided') : '...'}</p>
          
          <div className="flex justify-center md:justify-start gap-4">
             <div className="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2.5 rounded-2xl">
              <div>
                <span className="text-xs uppercase font-bold tracking-widest text-muted-foreground">Account Status: </span>
                <span className="font-bold text-green-500 ml-1">Active</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="shrink-0">
          <Button variant="outline" className="rounded-2xl border-white/10 hover:bg-white/10 text-white">
            Edit Profile
          </Button>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <div className="space-y-4">
          <h2 className="text-sm uppercase font-bold tracking-widest text-muted-foreground pl-2">App Settings</h2>
          <div className="glass rounded-3xl overflow-hidden flex flex-col">
            <div className="p-6 flex items-center justify-between border-b border-white/5">
              <div className="flex items-center gap-4 text-white">
                <div className="p-3 bg-white/5 rounded-xl">
                  <Moon className="w-5 h-5 text-muted-foreground" />
                </div>
                <span className="font-semibold text-lg">Dark Mode</span>
              </div>
              {mounted && (
                <Switch 
                  checked={isDark} 
                  onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')} 
                />
              )}
            </div>
            
            <div 
              onClick={() => toast.info('Notifications settings coming soon')}
              className="p-6 flex items-center justify-between border-b border-white/5 cursor-pointer hover:bg-white/5 transition-colors group"
            >
              <div className="flex items-center gap-4 text-white">
                <div className="p-3 bg-white/5 rounded-xl group-hover:bg-primary/20 transition-colors">
                  <Bell className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <span className="font-semibold text-lg">Notifications</span>
              </div>
              <ChevronRight className="w-6 h-6 text-muted-foreground group-hover:text-white transition-colors" />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-sm uppercase font-bold tracking-widest text-muted-foreground pl-2">Account Security</h2>
          <div className="glass rounded-3xl overflow-hidden flex flex-col">
            <div 
              onClick={() => toast.info('Backup & Security settings coming soon')}
              className="p-6 flex items-center justify-between border-b border-white/5 cursor-pointer hover:bg-white/5 transition-colors group"
            >
              <div className="flex items-center gap-4 text-white">
                <div className="p-3 bg-white/5 rounded-xl group-hover:bg-green-500/20 transition-colors">
                  <Shield className="w-5 h-5 text-muted-foreground group-hover:text-green-500 transition-colors" />
                </div>
                <span className="font-semibold text-lg">Backup & Security</span>
              </div>
              <ChevronRight className="w-6 h-6 text-muted-foreground group-hover:text-white transition-colors" />
            </div>
            
            <div 
              onClick={() => toast.info('Account Preferences coming soon')}
              className="p-6 flex items-center justify-between border-b border-white/5 cursor-pointer hover:bg-white/5 transition-colors group"
            >
              <div className="flex items-center gap-4 text-white">
                <div className="p-3 bg-white/5 rounded-xl group-hover:bg-blue-500/20 transition-colors">
                  <Settings className="w-5 h-5 text-muted-foreground group-hover:text-blue-500 transition-colors" />
                </div>
                <span className="font-semibold text-lg">Account Preferences</span>
              </div>
              <ChevronRight className="w-6 h-6 text-muted-foreground group-hover:text-white transition-colors" />
            </div>
          </div>
        </div>
        
      </div>

      {/* Logout */}
      <div className="pt-8 flex justify-center">
        <Button 
          onClick={handleLogout}
          variant="outline" 
          className="w-full md:w-auto px-12 h-14 rounded-2xl border-destructive/30 text-destructive hover:bg-destructive/10 hover:text-destructive font-bold text-lg"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </Button>
      </div>

    </div>
  );
}
