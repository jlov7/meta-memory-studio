import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        default:
          "bg-accent text-white hover:bg-accent-hover",
        secondary:
          "bg-surface-raised text-foreground hover:bg-border",
        ghost:
          "text-muted-foreground hover:bg-surface-raised hover:text-foreground",
        danger:
          "bg-danger-muted text-danger hover:bg-danger hover:text-white",
        outline:
          "border border-border text-foreground hover:bg-surface-raised",
      },
      size: {
        default: "h-8 px-3 py-1",
        sm: "h-7 px-2 py-0.5 text-xs",
        lg: "h-10 px-4 py-2",
        icon: "h-8 w-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
