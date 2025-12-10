"use client";
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { apiClient } from "@/lib/api-client";
import { ImportResult, ValidationError } from "@/types/api";
import { MobileNavigation } from "@/components/mobile-navigation";

interface FileUploadState {
  isUploading: boolean;
  progress: number;
  result: ImportResult | null;
  error: string | null;
  fileName: string | null;
}

export default function ImportPage() {
  const [uploadState, setUploadState] = useState<FileUploadState>({
    isUploading: false,
    progress: 0,
    result: null,
    error: null,
    fileName: null,
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadState((prev) => ({
        ...prev,
        fileName: file.name,
        error: null,
        result: null,
      }));
    }
  };

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setUploadState((prev) => ({
        ...prev,
        error: "请选择要上传的文件",
      }));
      return;
    }

    setUploadState((prev) => ({
      ...prev,
      isUploading: true,
      progress: 0,
      error: null,
      result: null,
    }));

    try {
      // 读取文件内容
      const reader = new FileReader();
      reader.onload = async (event) => {
        try {
          const content = event.target?.result as string;
          const data = JSON.parse(content);

          if (!Array.isArray(data)) {
            throw new Error("文件内容必须是JSON数组格式");
          }

          // 模拟进度更新
          const progressInterval = setInterval(() => {
            setUploadState((prev) => {
              if (prev.progress >= 90) {
                clearInterval(progressInterval);
                return prev;
              }
              return {
                ...prev,
                progress: prev.progress + 10,
              };
            });
          }, 300);

          // 调用导入API
          const result = await apiClient.import.importBatch({
            records: data,
            batchSize: 1000,
          });

          clearInterval(progressInterval);

          setUploadState((prev) => ({
            ...prev,
            isUploading: false,
            progress: 100,
            result,
            error: null,
          }));
        } catch (err) {
          setUploadState((prev) => ({
            ...prev,
            isUploading: false,
            error: err instanceof Error ? err.message : "文件解析失败",
          }));
        }
      };

      reader.onerror = () => {
        setUploadState((prev) => ({
          ...prev,
          isUploading: false,
          error: "文件读取失败",
        }));
      };

      reader.readAsText(file);
    } catch (err) {
      setUploadState((prev) => ({
        ...prev,
        isUploading: false,
        error: err instanceof Error ? err.message : "上传失败",
      }));
    }
  };

  const handleReset = () => {
    setUploadState({
      isUploading: false,
      progress: 0,
      result: null,
      error: null,
      fileName: null,
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-center flex-1">数据导入</h1>
          <MobileNavigation />
        </div>

        <Card className="p-6">
          {/* 文件上传区域 */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">选择文件</h2>
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-6 mb-4">
              <input
                type="file"
                ref={fileInputRef}
                accept=".json"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-primary hover:text-primary/80 transition-colors flex flex-col items-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mb-2"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <span className="text-lg font-medium">
                  拖拽文件到此处或点击选择文件
                </span>
                <span className="text-sm text-muted-foreground mt-1">
                  支持 JSON 格式文件，单文件大小不超过 100MB
                </span>
              </label>
              {uploadState.fileName && (
                <div className="mt-4 text-center">
                  <p className="text-sm text-muted-foreground">已选择文件：</p>
                  <p className="font-medium">{uploadState.fileName}</p>
                </div>
              )}
            </div>
          </div>

          {/* 上传控制按钮 */}
          <div className="flex gap-4 mb-6">
            <Button
              onClick={handleUpload}
              disabled={uploadState.isUploading || !uploadState.fileName}
              className="flex-1"
            >
              {uploadState.isUploading ? "上传中..." : "开始导入"}
            </Button>
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={uploadState.isUploading}
            >
              重置
            </Button>
          </div>

          {/* 进度显示 */}
          {uploadState.isUploading && (
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">导入进度</span>
                <span className="text-sm font-medium">
                  {uploadState.progress}%
                </span>
              </div>
              <Progress value={uploadState.progress} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                正在导入数据，请耐心等待...
              </p>
            </div>
          )}

          {/* 错误信息 */}
          {uploadState.error && (
            <Alert variant="destructive" className="mb-6">
              <AlertTitle>导入失败</AlertTitle>
              <AlertDescription>{uploadState.error}</AlertDescription>
            </Alert>
          )}

          {/* 导入结果 */}
          {uploadState.result && (
            <div className="mt-6">
              <Alert
                variant={
                  uploadState.result.failureCount > 0 ? "warning" : "success"
                }
                className="mb-4"
              >
                <AlertTitle>
                  {uploadState.result.failureCount > 0
                    ? "导入完成，但存在错误"
                    : "导入成功"}
                </AlertTitle>
                <AlertDescription>
                  成功导入 {uploadState.result.successCount} 条记录，失败{" "}
                  {uploadState.result.failureCount} 条记录
                </AlertDescription>
              </Alert>

              {/* 错误列表 */}
              {uploadState.result.errors.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-lg font-semibold mb-3">导入错误详情</h3>
                  <div className="max-h-60 overflow-y-auto rounded-lg border p-4">
                    {uploadState.result.errors.map(
                      (error: ValidationError, index: number) => (
                        <div
                          key={index}
                          className="mb-2 pb-2 border-b last:border-b-0 last:mb-0 last:pb-0"
                        >
                          <p className="text-sm font-medium">
                            记录 {error.recordIndex + 1}
                          </p>
                          <p className="text-sm text-destructive">
                            <span className="font-medium">{error.field}:</span>{" "}
                            {error.message}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
