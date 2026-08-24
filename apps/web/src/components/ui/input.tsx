import * as React from "react";

import { cn } from "@/lib/utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full min-w-0 rounded-xl border border-transparent bg-[#f4f6f1] px-4 py-2 text-base font-medium outline-none placeholder:text-[#84908d] focus-visible:border-[#82b9aa] focus-visible:ring-2 focus-visible:ring-[#82b9aa]/35 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
