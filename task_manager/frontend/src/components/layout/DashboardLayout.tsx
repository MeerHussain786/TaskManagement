import { Sidebar } from "./Sidebar";


export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen w-full flex overflow-hidden bg-background">
      
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden relative">
        <main className="flex-1 overflow-y-auto custom-scrollbar">
          {children}
        </main>
        
      </div>
      
    </div>
  )
}
