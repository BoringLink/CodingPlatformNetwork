import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">
          交互网络可视化系统
        </h1>
        <p className="text-center text-muted-foreground mb-8">
          基于交互网络的可视化分析平台
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild>
            <Link href="/graph">开始使用</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/reports">了解更多</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
