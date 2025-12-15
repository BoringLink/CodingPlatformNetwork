import * as React from "react";

import { cn } from "@/lib/utils";

const Progress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value: number;
    max?: number;
  }
>(({ className, value, max = 100, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
        className
      )}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-primary transition-all duration-300 ease-out"
        style={{
          transform: `translateX(-${100 - (value / max) * 100}%)`,
        }}
      />
    </div>
  );
});
Progress.displayName = "Progress";

export { Progress };
