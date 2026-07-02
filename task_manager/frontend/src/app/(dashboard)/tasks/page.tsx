"use client"

import { MoreHorizontal, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useListTasksApiV1TasksGet } from "@/services/api/generated/tasks/tasks";
import { TaskResponse } from "@/services/api/generated/models";
import Link from "next/link";

export default function KanbanBoard() {
  const { data: tasksResponse, isLoading } = useListTasksApiV1TasksGet({
    page_size: 100,
  });

  const tasks = tasksResponse?.items || [];

  // Map tasks to columns based on completion status since we don't have an explicit 'status' field yet.
  const columns = [
    {
      title: "To Do",
      color: "border-blue-500/30",
      bg: "bg-blue-500/10",
      tasks: tasks.filter(t => !t.completed)
    },
    {
      title: "Done",
      color: "border-green-500/30",
      bg: "bg-green-500/10",
      tasks: tasks.filter(t => t.completed)
    }
  ];

  const getPriorityColor = (priority?: string) => {
    if (priority === 'high' || priority === 'critical') return 'text-red-500';
    if (priority === 'medium') return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <div className="p-8 h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500 min-h-screen">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Project Board</h1>
          <p className="text-base text-muted-foreground mt-1">Manage your workflow and track progress.</p>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="h-12 px-6 rounded-full border-white/10 hover:bg-white/5 text-white font-medium">
            Filter
          </Button>
          <Link href="/add" className="inline-flex items-center justify-center h-12 px-6 rounded-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white font-bold shadow-lg shadow-primary/20 cursor-pointer">
            <Plus className="w-5 h-5 mr-2" />
            New Task
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="flex-1 flex justify-center items-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
        </div>
      ) : (
        /* Kanban Columns */
        <div className="flex-1 overflow-x-auto pb-4 custom-scrollbar">
          <div className="flex gap-6 h-full min-w-max items-start">
            
            {columns.map((col) => (
              <div key={col.title} className={`w-[350px] glass rounded-3xl p-5 flex flex-col ${col.color} border-t-4 max-h-[calc(100vh-200px)]`}>
                
                <div className="flex justify-between items-center mb-5 px-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-white">{col.title}</h3>
                    <span className={`text-sm px-3 py-1 rounded-full ${col.bg} text-white/90 font-bold`}>
                      {col.tasks.length}
                    </span>
                  </div>
                  <button className="text-muted-foreground hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg">
                    <MoreHorizontal className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex flex-col gap-4 overflow-y-auto custom-scrollbar pr-2 flex-1">
                  {col.tasks.map((task: TaskResponse) => (
                    <Link href={`/tasks/${task.id}`} key={task.id} className="block">
                      <div className="bg-black/20 border border-white/10 p-5 rounded-2xl cursor-pointer hover:border-primary/50 hover:bg-white/5 transition-all group">
                        <div className="flex justify-between items-start mb-3">
                          <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-white/10 text-white/90">
                            {task.completed ? 'Done' : 'Pending'}
                          </span>
                        </div>
                        
                        <h4 className={`text-lg font-semibold text-white mb-4 leading-snug ${task.completed ? 'line-through text-white/50' : ''}`}>
                          {task.title}
                        </h4>
                        
                        <div className="flex justify-between items-center mt-auto pt-4 border-t border-white/5">
                          <div className="flex -space-x-2">
                            <div className="w-8 h-8 rounded-full bg-primary border-2 border-background" />
                          </div>
                          <span className={`text-xs font-bold uppercase tracking-wider bg-white/5 px-3 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                  
                  {col.tasks.length === 0 && (
                    <div className="text-center text-muted-foreground py-8 border border-white/5 border-dashed rounded-2xl">
                      No tasks in this column.
                    </div>
                  )}
                </div>
                
                <Link href="/add" className="inline-flex items-center justify-center mt-4 w-full py-6 gap-2 text-sm font-semibold text-muted-foreground hover:text-white bg-black/20 hover:bg-white/10 border border-white/5 border-dashed rounded-xl transition-all cursor-pointer">
                  <Plus className="w-5 h-5" /> Add Task
                </Link>
              </div>
            ))}

          </div>
        </div>
      )}
      
    </div>
  );
}
