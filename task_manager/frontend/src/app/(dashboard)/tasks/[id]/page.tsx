"use client"

import { useState } from "react";
import { ArrowLeft, Clock, Calendar, Paperclip, MessageSquare, Play, CheckCircle2, Circle, Loader2, Tag, Repeat, X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { useGetTaskApiV1TasksTaskIdGet, useUpdateTaskApiV1TasksTaskIdPut } from "@/services/api/generated/tasks/tasks";
import { useQueryClient } from "@tanstack/react-query";
import { use } from "react";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

export default function TaskDetails({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: task, isLoading, isError } = useGetTaskApiV1TasksTaskIdGet(id);
  const updateMutation = useUpdateTaskApiV1TasksTaskIdPut();
  
  const [newSubtask, setNewSubtask] = useState("");

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[50vh]">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !task) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[50vh] space-y-4">
        <h2 className="text-2xl font-bold text-white">Task not found</h2>
        <Button variant="outline" onClick={() => router.back()}>Go Back</Button>
      </div>
    );
  }

  // Type cast for extended fields since they might not be strongly typed yet if api.ts hasn't rebuilt properly
  const t = task as any;
  const subtasks: any[] = t.subtasks || [];
  const tags: string[] = t.tags || [];

  const handleAddSubtask = () => {
    if (!newSubtask.trim()) return;
    const updatedSubtasks = [...subtasks, { title: newSubtask.trim(), completed: false }];
    updateMutation.mutate({
      taskId: id,
      data: { subtasks: updatedSubtasks } as any
    }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks', id] });
        setNewSubtask("");
      }
    });
  };

  const handleToggleSubtask = (index: number) => {
    const updatedSubtasks = [...subtasks];
    updatedSubtasks[index].completed = !updatedSubtasks[index].completed;
    updateMutation.mutate({
      taskId: id,
      data: { subtasks: updatedSubtasks } as any
    }, {
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks', id] })
    });
  };

  const handleRemoveSubtask = (index: number) => {
    const updatedSubtasks = subtasks.filter((_, i) => i !== index);
    updateMutation.mutate({
      taskId: id,
      data: { subtasks: updatedSubtasks } as any
    }, {
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks', id] })
    });
  };

  const completedCount = subtasks.filter(s => s.completed).length;

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 min-h-screen">
      
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()} className="rounded-full hover:bg-white/10">
            <ArrowLeft className="w-6 h-6" />
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-white tracking-tight">{task.title}</h1>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Description */}
            <div className="space-y-3">
              <h3 className="text-sm uppercase font-bold text-muted-foreground tracking-widest pl-1">Description</h3>
              <div className="glass p-6 rounded-3xl text-base text-white/90 leading-relaxed min-h-[150px]">
                {task.description || "No description provided."}
              </div>
            </div>

            {/* Subtasks */}
            <div className="space-y-4">
              <div className="flex items-center justify-between pl-1">
                <h3 className="text-sm uppercase font-bold text-muted-foreground tracking-widest">Subtasks</h3>
                <span className="text-sm font-medium text-white/50 bg-white/5 px-3 py-1 rounded-full">{completedCount}/{subtasks.length} Completed</span>
              </div>
              <div className="glass p-6 rounded-3xl space-y-4">
                
                {/* Subtask List */}
                <div className="space-y-2">
                  {subtasks.length === 0 ? (
                    <div className="text-center text-muted-foreground italic py-4">No subtasks added.</div>
                  ) : (
                    subtasks.map((st, i) => (
                      <div key={i} className={cn("flex items-center justify-between p-3 rounded-xl border transition-colors", st.completed ? "bg-white/5 border-white/5" : "bg-black/20 border-white/10")}>
                        <div className="flex items-center gap-3">
                          <button onClick={() => handleToggleSubtask(i)} className={cn("transition-colors", st.completed ? "text-primary" : "text-muted-foreground hover:text-white")}>
                            {st.completed ? <CheckCircle2 className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
                          </button>
                          <span className={cn("text-sm font-medium", st.completed ? "line-through text-white/40" : "text-white")}>{st.title}</span>
                        </div>
                        <button onClick={() => handleRemoveSubtask(i)} className="text-muted-foreground hover:text-destructive transition-colors">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Add Subtask */}
                <div className="flex items-center gap-2 pt-2">
                  <Input 
                    placeholder="Add new subtask..." 
                    value={newSubtask}
                    onChange={(e) => setNewSubtask(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAddSubtask()}
                    className="bg-black/20 border-white/10 rounded-xl"
                  />
                  <Button size="icon" onClick={handleAddSubtask} disabled={updateMutation.isPending || !newSubtask.trim()} className="bg-primary hover:bg-primary/90 text-black rounded-xl shrink-0">
                    {updateMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  </Button>
                </div>

              </div>
            </div>

          </div>

          {/* Sidebar Area */}
          <div className="space-y-6">
            
            {/* Status & Priority */}
            <div className="glass p-6 rounded-3xl space-y-6">
              <div className="space-y-3">
                <h3 className="text-xs uppercase font-bold text-muted-foreground tracking-widest">Status</h3>
                {task.completed ? (
                  <div className="bg-green-500/10 text-green-500 px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-wider flex items-center gap-2 border border-green-500/20">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    Completed
                  </div>
                ) : (
                  <div className="bg-yellow-500/10 text-yellow-500 px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-wider flex items-center gap-2 border border-yellow-500/20">
                    <div className="w-2 h-2 rounded-full bg-yellow-500" />
                    Pending
                  </div>
                )}
              </div>
              
              <div className="space-y-3">
                <h3 className="text-xs uppercase font-bold text-muted-foreground tracking-widest">Priority</h3>
                <div className={`px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-wider flex items-center gap-2 border ${
                  task.priority === 'high' || task.priority === 'critical' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                  task.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                  'bg-green-500/10 text-green-500 border-green-500/20'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    task.priority === 'high' || task.priority === 'critical' ? 'bg-red-500' :
                    task.priority === 'medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`} />
                  {task.priority}
                </div>
              </div>
            </div>

            {/* Metadata (Due Date, Repeat, Reminder) */}
            <div className="space-y-4">
              <div className="glass p-5 rounded-2xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-primary/20 p-2.5 rounded-xl text-primary">
                    <Calendar className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs uppercase font-bold text-muted-foreground tracking-widest">Due Date</div>
                    <span className="font-heading font-semibold text-lg text-white">{task.due_date ? format(new Date(task.due_date), "MMM d, yyyy") : 'No date'}</span>
                  </div>
                </div>
              </div>

              {t.recurring_rule && (
                <div className="glass p-5 rounded-2xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-secondary/20 p-2.5 rounded-xl text-secondary">
                      <Repeat className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs uppercase font-bold text-muted-foreground tracking-widest">Repeats</div>
                      <span className="font-heading font-semibold text-lg text-white capitalize">{t.recurring_rule}</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="glass p-5 rounded-2xl flex items-center justify-between bg-gradient-to-r from-primary/10 to-transparent border-primary/20">
                <div className="flex items-center gap-3">
                  <div className="bg-primary/20 p-2.5 rounded-xl text-primary">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs uppercase font-bold text-muted-foreground tracking-widest">Focus Timer</div>
                    <span className="font-mono font-bold text-lg text-white">00:00:00</span>
                  </div>
                </div>
                <button className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-black hover:bg-primary/90 transition-all hover:scale-110 shadow-lg shadow-primary/30">
                  <Play fill="currentColor" className="w-4 h-4 ml-0.5" />
                </button>
              </div>
            </div>

            {/* Tags */}
            {tags.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xs uppercase font-bold text-muted-foreground tracking-widest pl-1">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {tags.map(tag => (
                    <div key={tag} className="flex items-center gap-1.5 bg-accent/20 text-accent px-3 py-1.5 rounded-full text-xs font-bold border border-accent/30 tracking-wide">
                      <Tag className="w-3 h-3" />
                      {tag}
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
