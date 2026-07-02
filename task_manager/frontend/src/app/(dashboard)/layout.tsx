import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Suspense } from "react";

export const dynamic = 'force-dynamic';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardLayout>
      <Suspense fallback={<div>Loading...</div>}>
        {children}
      </Suspense>
    </DashboardLayout>
  );
}
