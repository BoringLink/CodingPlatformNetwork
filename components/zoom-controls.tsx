"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { ZoomIn, ZoomOut, Maximize2 } from "lucide-react";

interface ZoomControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetView: () => void;
  disabled?: boolean;
  className?: string;
}

export function ZoomControls({
  onZoomIn,
  onZoomOut,
  onResetView,
  disabled = false,
  className = "",
}: ZoomControlsProps) {
  return (
    <div
      className={`flex flex-col gap-2 p-2 bg-white/80 backdrop-blur-sm rounded-lg shadow-md border border-gray-200 ${className}`}
    >
      <Button
        variant="secondary"
        size="icon"
        onClick={onZoomIn}
        disabled={disabled}
        className="h-9 w-9"
        aria-label="放大"
      >
        <ZoomIn className="h-4 w-4" />
      </Button>
      <Button
        variant="secondary"
        size="icon"
        onClick={onZoomOut}
        disabled={disabled}
        className="h-9 w-9"
        aria-label="缩小"
      >
        <ZoomOut className="h-4 w-4" />
      </Button>
      <div className="border-t border-gray-200 my-1" />
      <Button
        variant="secondary"
        size="icon"
        onClick={onResetView}
        disabled={disabled}
        className="h-9 w-9"
        aria-label="重置视图"
      >
        <Maximize2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
