import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">
          教育知识图谱系统
        </h1>
        <p className="text-center text-muted-foreground mb-8">
          基于知识图谱的教育数据分析平台
        </p>
        <div className="flex gap-4 justify-center">
          <Button>开始使用</Button>
          <Button variant="outline">了解更多</Button>
        </div>
      </div>
    </div>
  );
}
