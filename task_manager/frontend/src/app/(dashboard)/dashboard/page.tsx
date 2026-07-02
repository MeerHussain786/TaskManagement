"use client"

import { useState } from "react";
import { Search, CheckCircle2, Calendar, Clock, Plus, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useListTasksApiV1TasksGet, useCompleteTaskApiV1TasksTaskIdCompletePatch } from "@/services/api/generated/tasks/tasks";
import { useAuthStore } from "@/store/useAuthStore";
import { useQueryClient } from "@tanstack/react-query";

export default function DashboardHome() {
  const [searchQuery, setSearchQuery] = useState("");
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  
  // Fetch tasks
  const { data: tasksResponse, isLoading } = useListTasksApiV1TasksGet({
    page_size: 100,
  });
  
  const completeTaskMutation = useCompleteTaskApiV1TasksTaskIdCompletePatch({
    mutation: {
      onSuccess: () => {
        // Invalidate and refetch tasks
        queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks'] });
      }
    }
  });

  const tasks = tasksResponse?.items || [];
  
  // Basic derived metrics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  
  // Sort tasks to show pending first, then complete
  const displayTasks = [...tasks].sort((a, b) => {
    if (a.completed === b.completed) return 0;
    return a.completed ? 1 : -1;
  });

  const handleToggleComplete = (taskId: string) => {
    completeTaskMutation.mutate({ taskId });
  };

  const getPriorityColor = (priority?: string) => {
    if (priority === 'high' || priority === 'critical') return 'text-red-500';
    if (priority === 'medium') return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
      
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight">
            👋 Good Morning, <span className="text-primary">{user?.email?.split('@')[0] || 'User'}</span>
          </h1>
          <p className="text-muted-foreground">Let's make today productive.</p>
        </div>

        <div className="relative w-full md:w-96">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground h-5 w-5" />
          <Input 
            placeholder="Search tasks..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 bg-white/5 border-white/10 rounded-full h-14 focus-visible:ring-primary text-base"
          />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-3xl flex items-center gap-6 group hover:bg-white/5 transition-colors">
          <div className="p-4 bg-primary/20 rounded-2xl group-hover:scale-110 transition-transform">
            <Calendar className="text-primary h-8 w-8" />
          </div>
          <div>
            <span className="text-4xl font-bold font-heading text-white block">
              {isLoading ? <Loader2 className="w-6 h-6 animate-spin mt-2" /> : totalTasks}
            </span>
            <span className="text-xs uppercase tracking-widest text-muted-foreground font-bold">Total Tasks</span>
          </div>
        </div>
        <div className="glass p-6 rounded-3xl flex items-center gap-6 group hover:bg-white/5 transition-colors">
          <div className="p-4 bg-green-500/20 rounded-2xl group-hover:scale-110 transition-transform">
            <CheckCircle2 className="text-green-500 h-8 w-8" />
          </div>
          <div>
            <span className="text-4xl font-bold font-heading text-white block">
              {isLoading ? <Loader2 className="w-6 h-6 animate-spin mt-2" /> : completedTasks}
            </span>
            <span className="text-xs uppercase tracking-widest text-muted-foreground font-bold">Completed</span>
          </div>
        </div>
        <div className="glass p-6 rounded-3xl flex items-center gap-6 group hover:bg-white/5 transition-colors">
          <div className="p-4 bg-yellow-500/20 rounded-2xl group-hover:scale-110 transition-transform">
            <Clock className="text-yellow-500 h-8 w-8" />
          </div>
          <div>
            <span className="text-4xl font-bold font-heading text-white block">
              {isLoading ? <Loader2 className="w-6 h-6 animate-spin mt-2" /> : pendingTasks}
            </span>
            <span className="text-xs uppercase tracking-widest text-muted-foreground font-bold">Pending</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Content Area (Tasks) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Your Tasks</h2>
            <Button variant="ghost" className="text-primary hover:text-primary/80 hover:bg-primary/10">
              View all
            </Button>
          </div>
          
          <div className="space-y-4">
            {isLoading && (
              <div className="flex justify-center p-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            )}
            
            {!isLoading && displayTasks.length === 0 && (
               <div className="glass p-12 rounded-3xl text-center text-muted-foreground">
                 <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                 <p>No tasks found. Time to create one!</p>
               </div>
            )}

            {displayTasks.filter(t => t.title.toLowerCase().includes(searchQuery.toLowerCase())).map((task) => (
              <div key={task.id} className="glass p-5 rounded-2xl flex items-center justify-between group hover:bg-white/10 hover:border-primary/50 transition-all">
                <div className="flex items-center gap-4 cursor-pointer" onClick={() => handleToggleComplete(task.id)}>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${task.completed ? 'bg-green-500/20 border-green-500' : 'border-muted-foreground group-hover:border-primary'}`}>
                    {task.completed && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                    {completeTaskMutation.isPending && completeTaskMutation.variables?.taskId === task.id && (
                      <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />
                    )}
                  </div>
                  <Link href={`/tasks/${task.id}`}>
                    <span className={`text-lg font-medium hover:text-primary transition-colors ${task.completed ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                      {task.title}
                    </span>
                  </Link>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/5">
                    <div className={`w-2 h-2 rounded-full ${getPriorityColor(task.priority).replace('text-', 'bg-')}`} />
                    <span className="text-xs uppercase font-bold tracking-wider">{task.priority}</span>
                  </div>
                  <Link href={`/tasks/${task.id}`}>
                    <ChevronRight className="w-5 h-5 text-muted-foreground opacity-0 -ml-2 group-hover:opacity-100 group-hover:translate-x-1 transition-all cursor-pointer" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Area (Upcoming & Quick Add) */}
        <div className="space-y-6">
          <Link href="/add" className="inline-flex items-center justify-center w-full rounded-2xl h-16 bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white shadow-lg shadow-primary/20 border-0 group cursor-pointer">
            <Plus className="mr-2 h-6 w-6 group-hover:scale-125 transition-transform" />
            <span className="font-heading font-bold text-lg tracking-wide uppercase">New Task</span>
          </Link>

          <div className="glass p-6 rounded-3xl space-y-6">
            <h2 className="text-xl font-semibold">Upcoming</h2>
            
            <div className="space-y-4">
              <div className="p-4 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-between cursor-pointer hover:bg-white/10 hover:border-white/10 transition-all group">
                <div className="flex items-center gap-4">
                  <div className="bg-primary/20 p-3 rounded-xl text-primary">
                    <Calendar className="h-6 w-6" />
                  </div>
                  <div>
                    <span className="font-medium text-white block">Tomorrow</span>
                    <span className="text-xs text-muted-foreground">4 tasks</span>
                  </div>
                </div>
                <ChevronRight className="text-muted-foreground group-hover:text-white transition-colors" />
              </div>
              
              <div className="p-4 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-between cursor-pointer hover:bg-white/10 hover:border-white/10 transition-all group">
                <div className="flex items-center gap-4">
                  <div className="bg-secondary/20 p-3 rounded-xl text-secondary">
                    <Calendar className="h-6 w-6" />
                  </div>
                  <div>
                    <span className="font-medium text-white block">This Week</span>
                    <span className="text-xs text-muted-foreground">12 tasks</span>
                  </div>
                </div>
                <ChevronRight className="text-muted-foreground group-hover:text-white transition-colors" />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
