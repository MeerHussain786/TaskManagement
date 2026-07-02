"use client"

import { CheckCircle2, Clock, Zap, Target, TrendingUp, BarChart, Loader2, AlertCircle } from "lucide-react";
import { useListTasksApiV1TasksGet } from "@/services/api/generated/tasks/tasks";

export default function AnalyticsView() {
  const { data: tasksResponse, isLoading } = useListTasksApiV1TasksGet({
    page_size: 100,
  });

  const tasks = tasksResponse?.items || [];
  
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  
  const completionPercentage = totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100);
  
  const highPriorityTasks = tasks.filter(t => (t.priority === 'high' || t.priority === 'critical') && !t.completed).length;
  
  const today = new Date();
  today.setHours(0,0,0,0);
  const overdueTasks = tasks.filter(t => {
    if (t.completed || !t.due_date) return false;
    return new Date(t.due_date) < today;
  }).length;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen w-full">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 max-w-7xl mx-auto min-h-screen">
      
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="p-4 bg-primary/20 rounded-2xl">
          <BarChart className="w-8 h-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Analytics Overview</h1>
          <p className="text-muted-foreground text-base">Your actual task metrics from the database.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Highlights */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Overall Progress Bar */}
          <div className="glass p-8 rounded-3xl space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <h2 className="text-sm uppercase font-bold tracking-widest text-muted-foreground mb-1">Overall Task Progress</h2>
                <div className="flex items-center gap-2 text-primary text-sm font-medium">
                  <span>Based on all recorded tasks</span>
                </div>
              </div>
              <span className="text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                {completionPercentage}%
              </span>
            </div>
            
            <div className="h-6 bg-white/5 rounded-full overflow-hidden border border-white/10 shadow-inner">
              <div 
                className="h-full bg-gradient-to-r from-primary to-secondary rounded-full relative transition-all duration-1000"
                style={{ width: `${completionPercentage}%` }}
              >
                <div className="absolute top-0 bottom-0 left-0 right-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSJ0cmFuc3BhcmVudCI+PC9yZWN0Pgo8bGluZSB4MT0iMCIgeTE9IjQiIHgyPSI0IiB5Mj0iMCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLW9wYWNpdHk9IjAuNSIgc3Ryb2tlLXdpZHRoPSIxIj48L2xpbmU+Cjwvc3ZnPg==')] opacity-30"></div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Completed */}
            <div className="glass p-6 rounded-3xl flex flex-col gap-4 relative overflow-hidden group hover:bg-white/5 transition-colors">
              <div className="absolute -right-10 -top-10 w-32 h-32 bg-green-500/10 rounded-full blur-3xl group-hover:bg-green-500/20 transition-colors" />
              <div className="bg-green-500/20 w-fit p-3 rounded-2xl">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
              <div>
                <span className="text-5xl font-heading font-bold text-white block mb-1">{completedTasks}</span>
                <div className="text-sm uppercase font-bold tracking-widest text-muted-foreground">Tasks Completed</div>
              </div>
            </div>

            {/* Pending */}
            <div className="glass p-6 rounded-3xl flex flex-col gap-4 relative overflow-hidden group hover:bg-white/5 transition-colors">
              <div className="absolute -right-10 -top-10 w-32 h-32 bg-yellow-500/10 rounded-full blur-3xl group-hover:bg-yellow-500/20 transition-colors" />
              <div className="bg-yellow-500/20 w-fit p-3 rounded-2xl">
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
              <div>
                <span className="text-5xl font-heading font-bold text-white block mb-1">{pendingTasks}</span>
                <div className="text-sm uppercase font-bold tracking-widest text-muted-foreground">Tasks Pending</div>
              </div>
            </div>

          </div>
        </div>

        {/* Side Stats */}
        <div className="space-y-8">
          
          {/* High Priority */}
          <div className="glass p-8 rounded-3xl flex flex-col justify-center items-center text-center relative overflow-hidden group h-[220px] hover:bg-white/5 transition-colors">
            <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent opacity-50" />
            <Target className="w-12 h-12 text-accent mb-6" />
            <div>
              <span className="text-6xl font-heading font-bold text-white tracking-tighter">{highPriorityTasks}</span>
              <div className="text-sm uppercase font-bold tracking-widest text-muted-foreground mt-3">High Priority Pending</div>
            </div>
          </div>

          {/* Overdue */}
          <div className="glass p-8 rounded-3xl flex flex-col justify-center items-center text-center relative overflow-hidden group h-[220px] hover:bg-white/5 transition-colors">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent opacity-50" />
            <AlertCircle className="w-12 h-12 text-red-500 mb-6" />
            <div>
              <span className="text-6xl font-heading font-bold text-red-500 tracking-tighter">{overdueTasks}</span>
              <div className="text-sm uppercase font-bold tracking-widest text-muted-foreground mt-3">Tasks Overdue</div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
