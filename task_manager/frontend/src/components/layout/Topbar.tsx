import { UserNav } from './UserNav';
import { ThemeToggle } from '../ThemeToggle';

export function Topbar() {
  return (
    <header className="h-16 border-b bg-card flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4 md:hidden">
        <span className="font-bold">TaskMaster</span>
      </div>
      <div className="flex items-center gap-4 ml-auto">
        <ThemeToggle />
        <UserNav />
      </div>
    </header>
  );
}
