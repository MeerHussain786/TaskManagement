"use client"

import { Button } from "@/components/ui/button"
import { AlertCircle } from "lucide-react"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 text-center">
      <AlertCircle className="h-12 w-12 text-destructive mb-4" />
      <h2 className="text-2xl font-bold mb-2">Something went wrong!</h2>
      <p className="text-muted-foreground mb-6 max-w-md">
        An unexpected error occurred. Our team has been notified.
      </p>
      <div className="flex gap-4">
        <Button onClick={() => window.location.href = '/'}>Go Home</Button>
        <Button variant="outline" onClick={() => reset()}>Try again</Button>
      </div>
    </div>
  )
}
