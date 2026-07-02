"use client"

import { Button } from "@/components/ui/button"
import { FileQuestion } from "lucide-react"
import Link from "next/link"

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 text-center">
      <FileQuestion className="h-16 w-16 text-muted-foreground mb-4" />
      <h2 className="text-3xl font-bold mb-2">Page Not Found</h2>
      <p className="text-muted-foreground mb-6 max-w-md">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Button render={(props) => <Link href="/" {...props}>Return Home</Link>} />
    </div>
  )
}
