"use client";

import * as React from "react";
import { ChevronDownIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { DateRange } from "react-day-picker";
import { formatDate } from "@/lib/utils";

export function DatePicker({
  title,
  dateRange,
  onDateRangeChange,
}: {
  title: string;
  dateRange?: DateRange;
  onDateRangeChange: (date: DateRange | undefined) => void;
}) {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="flex flex-col gap-3 w-full">
      <Label htmlFor="date" className="px-1">
        {title}
      </Label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            id="date"
            className="w-full justify-between font-normal shadow-md hover:shadow-lg transition-all"
          >
            {dateRange
              ? `${formatDate(dateRange.from)} - ${formatDate(dateRange.to)}`
              : "选择日期"}
            <ChevronDownIcon />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="w-auto overflow-hidden p-0 bg-white dark:bg-black"
          align="start"
        >
          <Calendar
            className="w-60"
            mode="range"
            selected={dateRange}
            captionLayout="dropdown"
            onSelect={(date) => {
              onDateRangeChange(date);
              setOpen(false);
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
