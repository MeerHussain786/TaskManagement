"use client"

import { ColumnDef } from "@tanstack/react-table"
import { TaskResponse } from "@/services/api/generated/models"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { MoreHorizontal, Trash, Edit, CheckSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { 
  useDeleteTaskApiV1TasksTaskIdDelete, 
  useCompleteTaskApiV1TasksTaskIdCompletePatch,
  useUpdateTaskApiV1TasksTaskIdPut
} from "@/services/api/generated/tasks/tasks"
import { toast } from "sonner"
import { useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

const TaskCompletionCell = ({ task }: { task: TaskResponse }) => {
  const queryClient = useQueryClient()
  const updateMutation = useUpdateTaskApiV1TasksTaskIdPut()
  const completeMutation = useCompleteTaskApiV1TasksTaskIdCompletePatch()
  
  const [isUpdating, setIsUpdating] = useState(false)

  const handleToggleComplete = async (checked: boolean) => {
    setIsUpdating(true)
    try {
      if (checked) {
        await completeMutation.mutateAsync({ taskId: task.id })
        toast.success("Task completed! 🕸️")
      } else {
        await updateMutation.mutateAsync({ 
          taskId: task.id, 
          data: { completed: false }
        })
        toast.success("Task reopened")
      }
      queryClient.invalidateQueries()
    } catch (error) {
      toast.error("Failed to update task")
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <div className="flex items-center space-x-2">
      <Checkbox 
        checked={task.completed}
        disabled={isUpdating}
        className="w-5 h-5 border-2 border-primary data-[state=checked]:bg-primary data-[state=checked]:text-white transition-all"
        onCheckedChange={(checked) => handleToggleComplete(!!checked)} 
      />
      <Badge variant={task.completed ? "default" : "secondary"}>
        {task.completed ? "Done" : "Pending"}
      </Badge>
    </div>
  )
}

export const columns: ColumnDef<TaskResponse>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        indeterminate={!table.getIsAllPageRowsSelected() && table.getIsSomePageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "completed",
    header: "Status",
    cell: ({ row }) => <TaskCompletionCell task={row.original} />,
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => {
      const isCompleted = row.original.completed
      return (
        <div className={`font-medium text-lg transition-all ${isCompleted ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
          {row.getValue("title")}
        </div>
      )
    },
  },
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => {
      const priority = row.getValue("priority") as string
      const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
        low: "secondary",
        medium: "outline",
        high: "default",
        critical: "destructive",
      }
      return <Badge variant={variants[priority] || "outline"} className="capitalize">{priority}</Badge>
    },
  },
  {
    accessorKey: "due_date",
    header: "Due Date",
    cell: ({ row }) => {
      const dueDate = row.getValue("due_date") as string | null
      return dueDate ? new Intl.DateTimeFormat('en-US', { month: 'short', day: '2-digit', year: 'numeric' }).format(new Date(dueDate)) : "-"
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const task = row.original
      const queryClient = useQueryClient()
      const deleteMutation = useDeleteTaskApiV1TasksTaskIdDelete()

      const handleDelete = async () => {
        try {
          await deleteMutation.mutateAsync({ taskId: task.id })
            toast.success("Task deleted successfully")
            queryClient.invalidateQueries()
        } catch (error) {
          toast.error("Failed to delete task")
        }
      }

      return (
        <DropdownMenu>
          <DropdownMenuTrigger
            render={(props) => (
              <Button variant="ghost" className="h-8 w-8 p-0" {...props}>
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            )}
          />
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => navigator.clipboard.writeText(task.id)}>
              Copy task ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive" onClick={handleDelete}>
              <Trash className="mr-2 h-4 w-4" />
              Delete Task
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]
