"use client"

import { useState, useEffect, useRef } from "react";
import { ArrowLeft, Calendar as CalendarIcon, Tag, Clock, Repeat, Mic, Check, Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useRouter, useSearchParams } from "next/navigation";
import { useCreateTaskApiV1TasksPost } from "@/services/api/generated/tasks/tasks";
import { useQueryClient } from "@tanstack/react-query";
import { TaskPriority } from "@/services/api/generated/models";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

// Minimal global typing for SpeechRecognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function AddTask() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  
  const initialDateParam = searchParams.get("date");
  const [dueDate, setDueDate] = useState<Date | undefined>(initialDateParam ? new Date(initialDateParam) : undefined);
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [recurringRule, setRecurringRule] = useState<string>("none");
  
  const [error, setError] = useState("");
  const [isListening, setIsListening] = useState(false);
  
  // Setup SpeechRecognition
  const recognitionRef = useRef<any>(null);
  
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        
        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript + " ";
            }
          }
          if (finalTranscript) {
            setDescription((prev) => (prev + " " + finalTranscript).trim());
          }
        };
        
        recognitionRef.current.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, []);

  const toggleListen = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsListening(true);
        } catch (e) {
          console.error(e);
        }
      } else {
        alert("Your browser does not support Speech Recognition.");
      }
    }
  };

  const createTaskMutation = useCreateTaskApiV1TasksPost({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['/api/v1/tasks'] });
        router.push('/dashboard');
      },
      onError: (err) => {
        setError("Failed to create task. Please try again.");
      }
    }
  });

  const priorities: { label: string, value: TaskPriority, color: string, bg: string, border: string }[] = [
    { label: "Low", value: "low", color: "text-green-500", bg: "bg-green-500/20", border: "border-green-500/30" },
    { label: "Medium", value: "medium", color: "text-yellow-500", bg: "bg-yellow-500/20", border: "border-yellow-500/30" },
    { label: "High", value: "high", color: "text-red-500", bg: "bg-red-500/20", border: "border-red-500/30" },
  ];

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const handleSave = () => {
    if (!title.trim()) {
      setError("Title is required");
      return;
    }
    
    setError("");
    createTaskMutation.mutate({
      data: {
        title: title.trim(),
        description: description.trim() || undefined,
        priority: priority,
        due_date: dueDate ? format(dueDate, "yyyy-MM-dd") : undefined,
        tags: tags.length > 0 ? tags : undefined,
        recurring_rule: recurringRule !== "none" ? recurringRule : undefined,
      } as any // using any to bypass type check temporarily if api.ts hasn't refreshed types properly
    });
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 min-h-screen">
      
      <div className="max-w-3xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()} className="rounded-full hover:bg-white/10">
            <ArrowLeft className="w-6 h-6" />
          </Button>
          <h1 className="text-3xl font-bold font-heading uppercase tracking-wide text-white">New Task</h1>
        </div>

        <div className="glass p-8 rounded-3xl space-y-8 border-primary/20">
          
          {error && (
            <div className="bg-destructive/20 text-destructive border border-destructive p-4 rounded-xl text-sm font-medium">
              {error}
            </div>
          )}
          
          {/* Title */}
          <div className="space-y-2">
            <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider pl-1">Title</label>
            <Input 
              placeholder="What needs to be done?" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-white/5 border-white/10 rounded-xl h-16 text-2xl px-4 focus-visible:ring-primary placeholder:text-muted-foreground/50 transition-colors font-heading"
            />
          </div>

          {/* Description */}
          <div className="space-y-2 relative">
            <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider pl-1">Description</label>
            <Textarea 
              placeholder="Add some details..." 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={cn("bg-white/5 border border-white/10 rounded-2xl min-h-[160px] resize-none focus-visible:ring-primary text-lg p-5", isListening && "border-primary shadow-[0_0_15px_rgba(255,255,0,0.5)]")}
            />
            <Button 
              size="icon" 
              variant="ghost" 
              onClick={toggleListen}
              className={cn("absolute bottom-4 right-4 rounded-full", isListening ? "bg-primary text-black hover:bg-primary/80 animate-pulse" : "hover:bg-white/10")}
            >
              <Mic className="w-5 h-5" />
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Quick Settings */}
            <div className="space-y-4">
              <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider pl-1">Schedule</label>
              <div className="grid grid-cols-2 gap-4">
                
                <Popover>
                  <PopoverTrigger className={cn("bg-black/20 p-4 rounded-2xl flex flex-col gap-2 hover:bg-white/5 cursor-pointer border border-white/5 transition-colors text-left", dueDate && "border-primary/50 bg-primary/5")}>
                    <CalendarIcon className="text-primary w-6 h-6" />
                    <div>
                      <div className="text-sm font-medium text-white">Due Date</div>
                      <div className="text-xs text-muted-foreground">{dueDate ? format(dueDate, "MMM d, yyyy") : "None"}</div>
                    </div>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={dueDate}
                      onSelect={setDueDate}
                    />
                  </PopoverContent>
                </Popover>
                
                <Select value={recurringRule} onValueChange={(val) => val && setRecurringRule(val)}>
                  <SelectTrigger className={cn("h-auto w-full bg-black/20 p-4 rounded-2xl flex flex-col items-start gap-2 hover:bg-white/5 cursor-pointer border border-white/5 transition-colors [&>svg]:hidden text-left", recurringRule !== 'none' && "border-secondary/50 bg-secondary/5")}>
                    <Repeat className="text-secondary w-6 h-6" />
                    <div>
                      <div className="text-sm font-medium text-white">Repeat</div>
                      <div className="text-xs text-muted-foreground capitalize">{recurringRule === 'none' ? 'None' : recurringRule}</div>
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Repeat</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>

              </div>
            </div>

            {/* Priority */}
            <div className="space-y-4">
              <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider pl-1">Priority</label>
              <div className="flex flex-col gap-3">
                {priorities.map((p) => (
                  <button
                    key={p.value}
                    onClick={() => setPriority(p.value)}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl border transition-all ${
                      priority === p.value 
                        ? `${p.bg} border-primary ${p.color}` 
                        : 'bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10'
                    }`}
                  >
                    <div className={`w-3 h-3 rounded-full ${p.bg.replace('/20', '')}`} />
                    <span className="font-bold">{p.label}</span>
                  </button>
                ))}
              </div>
            </div>

          </div>

          {/* Tags */}
          <div className="space-y-4 pt-4 border-t border-white/10">
            <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider pl-1">Tags</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {tags.map(tag => (
                <div key={tag} className="flex items-center gap-1 bg-accent/20 text-accent px-3 py-1.5 rounded-full text-sm font-medium border border-accent/30">
                  <Tag className="w-3 h-3" />
                  {tag}
                  <button onClick={() => removeTag(tag)} className="ml-1 hover:text-white transition-colors">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
            <Input 
              placeholder="Type a tag and press Enter..." 
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
              className="bg-black/20 border-white/10 rounded-xl"
            />
          </div>

          {/* Save Button */}
          <div className="pt-6">
            <Button 
              onClick={handleSave}
              disabled={createTaskMutation.isPending}
              className="w-full rounded-2xl h-16 bg-primary hover:bg-primary/90 text-black font-heading text-xl tracking-wide uppercase shadow-[0_0_20px_rgba(255,255,0,0.3)] transition-all group border-none"
            >
              {createTaskMutation.isPending ? (
                <Loader2 className="mr-3 w-6 h-6 animate-spin" />
              ) : (
                <Check className="mr-3 w-6 h-6 group-hover:scale-125 transition-transform" />
              )}
              Save Task
            </Button>
          </div>
          
        </div>
      </div>
    </div>
  );
}
