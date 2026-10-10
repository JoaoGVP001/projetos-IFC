import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-bold transition-colors outline-none disabled:pointer-events-none disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-[#82b9aa] focus-visible:ring-offset-2",
  {
    variants: {
      variant: {
        default: "bg-[#123b3b] text-white hover:bg-[#1d5150]",
        lime: "bg-[#d7ff75] text-[#163738] hover:bg-[#c9f05f]",
        outline: "border border-[#d9dfd8] bg-white text-[#64736f] hover:bg-[#e3eee3] hover:text-[#17423e]",
        ghost: "text-[#60716e] hover:bg-[#e9eee7] hover:text-[#173c3c]",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-lg px-3 text-xs",
        lg: "h-14 rounded-2xl px-7",
        icon: "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Component = asChild ? Slot : "button";

  return <Component className={cn(buttonVariants({ variant, size, className }))} {...props} />;
}

export { Button, buttonVariants };
