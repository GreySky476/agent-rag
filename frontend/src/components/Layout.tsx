import type { ReactNode } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import { useChatStore } from "../stores/chatStore";

interface Props {
  children: ReactNode;
}

export default function Layout({ children }: Props) {
  const sidebarOpen = useChatStore((s) => s.sidebarOpen);

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        {sidebarOpen && (
          <aside className="w-64 flex-shrink-0 border-r border-border">
            <Sidebar />
          </aside>
        )}
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
