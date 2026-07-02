"use client"

import { useState, useMemo } from "react";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useListTasksApiV1TasksGet } from "@/services/api/generated/tasks/tasks";
import { startOfMonth, endOfMonth, eachDayOfInterval, format, getDay, addMonths, subMonths, isSameDay, isToday } from "date-fns";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export default function CalendarView() {
  const router = useRouter();
  
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  const { data: tasksResponse, isLoading } = useListTasksApiV1TasksGet({
    page_size: 100 // Fetch a large amount to ensure we get tasks for the month
  });

  const tasks = tasksResponse?.items || [];

  const daysInMonth = useMemo(() => {
    const start = startOfMonth(currentMonth);
    const end = endOfMonth(currentMonth);
    return eachDayOfInterval({ start, end });
  }, [currentMonth]);

  const startDayOfWeek = getDay(startOfMonth(currentMonth)); // 0 = Sun, 1 = Mon

  const tasksForSelected = useMemo(() => {
    return tasks.filter(t => t.due_date && isSameDay(new Date(t.due_date), selectedDate));
  }, [tasks, selectedDate]);

  const handlePrevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));
  const handleNextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const handleToday = () => {
    setCurrentMonth(new Date());
    setSelectedDate(new Date());
  };

  const handleAddTaskForSelected = () => {
    router.push(`/add?date=${format(selectedDate, "yyyy-MM-dd")}`);
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-7xl mx-auto min-h-screen">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-black/20 p-6 rounded-3xl border border-white/5 gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary/20 rounded-xl">
            <CalendarIcon className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight font-heading">{format(currentMonth, "MMMM yyyy")}</h1>
            <p className="text-muted-foreground text-sm font-medium tracking-wide uppercase">Schedule & Deadlines</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={handleToday} variant="outline" className="h-10 px-4 rounded-full border-white/10 hover:bg-white/10 text-white font-medium uppercase tracking-wide text-xs">
            Today
          </Button>
          <div className="flex gap-1 ml-2 bg-white/5 p-1 rounded-full border border-white/10">
            <Button onClick={handlePrevMonth} variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-white/10 text-white cursor-pointer">
              <ChevronLeft className="w-5 h-5" />
            </Button>
            <Button onClick={handleNextMonth} variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-white/10 text-white cursor-pointer">
              <ChevronRight className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Calendar Grid (Main) */}
        <div className="lg:col-span-3 glass p-8 rounded-3xl">
          <div className="grid grid-cols-7 gap-4 mb-6 text-center border-b border-white/10 pb-4">
            {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(day => (
              <div key={day} className="text-xs lg:text-sm font-bold text-muted-foreground uppercase tracking-widest">{day.slice(0,3)}</div>
            ))}
          </div>
          
          <div className="grid grid-cols-7 gap-4">
            {/* Empty cells before start of month */}
            {Array.from({ length: startDayOfWeek }).map((_, i) => (
              <div key={`empty-${i}`} className="min-h-[100px] lg:min-h-[120px] rounded-2xl bg-white/5 border border-white/5 border-dashed" />
            ))}
            
            {/* Days */}
            {daysInMonth.map(day => {
              const dayTasks = tasks.filter(t => t.due_date && isSameDay(new Date(t.due_date), day));
              const hasHighPriority = dayTasks.some(t => t.priority === 'high' || t.priority === 'critical');
              const hasNormalPriority = dayTasks.some(t => t.priority === 'low' || t.priority === 'medium');
              const isSelected = isSameDay(selectedDate, day);
              const isCurrentDay = isToday(day);

              return (
                <div 
                  key={day.toString()} 
                  onClick={() => setSelectedDate(day)}
                  className={cn(
                    "min-h-[100px] lg:min-h-[120px] p-2 lg:p-3 flex flex-col relative cursor-pointer rounded-2xl border transition-all",
                    isSelected 
                      ? "border-primary bg-primary/10 shadow-[0_0_20px_rgba(var(--primary),0.2)]" 
                      : "border-white/10 bg-black/20 hover:border-primary/50 hover:bg-white/5",
                    isCurrentDay && !isSelected && "border-secondary/50 bg-secondary/5"
                  )}
                >
                  <div className="flex justify-between items-start">
                    <span className={cn("text-lg font-bold font-mono", isSelected ? "text-primary" : isCurrentDay ? "text-secondary" : "text-white")}>
                      {format(day, "d")}
                    </span>
                  </div>
                  
                  {/* Indicators */}
                  <div className="mt-auto space-y-1">
                    {hasHighPriority && (
                      <div className="w-full h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" title="High Priority tasks" />
                    )}
                    {hasNormalPriority && (
                      <div className="w-full h-1.5 rounded-full bg-primary" title="Normal tasks" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sidebar / Selected Day Details */}
        <div className="space-y-6">
          <div className="glass p-6 rounded-3xl min-h-[400px] flex flex-col">
            <h2 className="text-xl font-bold border-b border-white/10 pb-4 mb-4 text-white font-heading">
              {format(selectedDate, "MMMM d")}
              <span className="block text-sm text-muted-foreground font-normal mt-1 uppercase tracking-wider">{tasksForSelected.length} tasks scheduled</span>
            </h2>
            
            <div className="space-y-4 flex-1">
              {isLoading ? (
                <div className="flex justify-center py-10"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : tasksForSelected.map((task) => (
                <div key={task.id} onClick={() => router.push(`/tasks/${task.id}`)} className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-primary/50 hover:bg-white/10 transition-all cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className={cn("w-2 h-12 rounded-full shrink-0", (task.priority === 'high' || task.priority === 'critical') ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" : "bg-primary")} />
                    <div>
                      <div className="font-semibold text-white leading-tight mb-1 font-heading">{task.title}</div>
                      <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{task.priority} Priority</div>
                    </div>
                  </div>
                </div>
              ))}
              
              {!isLoading && tasksForSelected.length === 0 && (
                <div className="text-center text-muted-foreground py-10 font-mono text-sm">
                  <p>No tasks scheduled.</p>
                </div>
              )}
            </div>
            
            <Button onClick={handleAddTaskForSelected} className="w-full mt-6 bg-primary/20 hover:bg-primary/30 border border-primary/50 text-primary font-bold tracking-wide uppercase rounded-xl h-12 cursor-pointer transition-colors">
              Add Task for {format(selectedDate, "MMM d")}
            </Button>
          </div>
          
          {/* Legend */}
          <div className="glass p-6 rounded-3xl flex flex-col gap-4">
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Legend</h3>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-primary" />
              <span className="text-sm text-white font-medium uppercase tracking-wide">Normal Task</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
              <span className="text-sm text-white font-medium uppercase tracking-wide">High Priority</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-secondary/50 border border-secondary" />
              <span className="text-sm text-white font-medium uppercase tracking-wide">Current Day</span>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}
