"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"

import { useLoginApiV1AuthLoginPost } from "@/services/api/generated/authentication/authentication"
import { useAuthStore } from "@/store/useAuthStore"
import { customInstance } from "@/services/api/axios-instance"
import { UserResponse } from "@/services/api/generated/models"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import Link from "next/link"

const loginSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(1, { message: "Password is required" }),
})

export default function LoginPage() {
  const router = useRouter()
  const setTokens = useAuthStore((state) => state.setTokens)
  const setUser = useAuthStore((state) => state.setUser)

  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const loginMutation = useLoginApiV1AuthLoginPost()

  async function onSubmit(values: z.infer<typeof loginSchema>) {
    try {
      const response = await loginMutation.mutateAsync({ data: values })
      setTokens(response.access_token, response.refresh_token)
      
      const userProfile = await customInstance<UserResponse>({ url: '/api/v1/users/me', method: 'GET' })
      setUser(userProfile)
      
      document.cookie = `token=${response.access_token}; path=/; max-age=${response.expires_in}; samesite=lax`;

      toast.success("Login successful")
      router.push("/dashboard")
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Invalid credentials. Please try again.")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-animated-gradient p-4">
      {/* Decorative background elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/30 rounded-full blur-[100px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[100px] pointer-events-none mix-blend-screen" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md relative z-10"
      >
        <div className="glass-dark rounded-3xl p-8 shadow-2xl">
          <div className="text-center mb-8 space-y-2">
            <motion.h1 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-4xl font-bold tracking-tight text-white"
            >
              Welcome back
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="text-white/70"
            >
              Sign in to manage your tasks beautifully.
            </motion.p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-white/90">Email</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="m@example.com" 
                        {...field} 
                        className="bg-white/5 border-white/10 text-white placeholder:text-white/40 focus-visible:ring-primary h-12 rounded-xl transition-all hover:bg-white/10"
                      />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-white/90">Password</FormLabel>
                    <FormControl>
                      <Input 
                        type="password" 
                        placeholder="••••••••" 
                        {...field} 
                        className="bg-white/5 border-white/10 text-white placeholder:text-white/40 focus-visible:ring-primary h-12 rounded-xl transition-all hover:bg-white/10"
                      />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
              <motion.div
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                className="pt-4"
              >
                <Button 
                  className="w-full h-12 rounded-xl bg-gradient-to-r from-primary to-blue-500 hover:from-primary/90 hover:to-blue-500/90 text-white font-semibold text-lg shadow-lg shadow-primary/25 transition-all" 
                  type="submit" 
                  disabled={loginMutation.isPending}
                >
                  {loginMutation.isPending ? "Signing in..." : "Sign in"}
                </Button>
              </motion.div>
            </form>
          </Form>

          <div className="mt-8 text-center text-sm text-white/60">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-white font-medium hover:text-primary transition-colors">
              Sign up
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

