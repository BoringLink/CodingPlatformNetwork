import * as XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

/**
 * Excel文件读取工具类
 */
export class ExcelReaderUtil {
  /**
   * 读取Excel文件
   * @param filePath 文件路径
   * @returns 工作表数据
   */
  static readExcelFile(filePath: string): Record<string, any[]> {
    if (!fs.existsSync(filePath)) {
      throw new Error(`文件不存在: ${filePath}`);
    }

    const extension = this.getFileExtension(filePath);
    
    // 使用xlsx MCP处理.xlsx文件
    if (extension === '.xlsx' || extension === '.xlsm') {
      return this.readXlsxFileWithMCP(filePath);
    }
    // 使用Python脚本处理.xls文件
    else if (extension === '.xls') {
      return this.readXlsFileWithPython(filePath);
    }
    else {
      throw new Error(`不支持的文件格式: ${extension}`);
    }
  }

  /**
   * 使用xlsx MCP读取.xlsx文件
   * @param filePath 文件路径
   * @returns 工作表数据
   */
  private static readXlsxFileWithMCP(filePath: string): Record<string, any[]> {
    const workbook = XLSX.readFile(filePath);
    const sheets: Record<string, any[]> = {};

    workbook.SheetNames.forEach(sheetName => {
      const worksheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(worksheet, {
        header: 1,
        defval: '',
      });

      if (data.length > 0) {
        const headers = data[0] as any[];
        const rows = data.slice(1);
        
        const formattedData = rows.map(row => {
          const rowData: any = {};
          if (headers && Array.isArray(headers)) {
            headers.forEach((header: any, index: number) => {
              rowData[header] = row[index] || '';
            });
          }
          return rowData;
        });

        sheets[sheetName] = formattedData;
      }
    });

    return sheets;
  }

  /**
   * 使用Python脚本读取.xls文件
   * @param filePath 文件路径
   * @returns 工作表数据
   */
  private static readXlsFileWithPython(filePath: string): Record<string, any[]> {
    try {
      // 创建临时Python脚本
      const pythonScript = `
import pandas as pd
import json
import sys

def read_xls_file(file_path):
    try:
        # 读取所有工作表
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        result = {}
        
        for sheet_name, df in all_sheets.items():
            # 转换为字典列表
            records = df.to_dict('records')
            # 处理空值
            cleaned_records = []
            for record in records:
                cleaned_record = {}
                for key, value in record.items():
                    if pd.isna(value):
                        cleaned_record[key] = ''
                    else:
                        cleaned_record[key] = value
                cleaned_records.append(cleaned_record)
            result[sheet_name] = cleaned_records
        
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({'error': '参数错误'}), file=sys.stderr)
        sys.exit(1)
    read_xls_file(sys.argv[1])
`;

      const scriptPath = path.join('/tmp', `read_xls_${Date.now()}.py`);
      fs.writeFileSync(scriptPath, pythonScript);

      // 执行Python脚本，使用虚拟环境
      const venvPath = path.join(process.cwd(), 'venv', 'bin', 'python3');
      let output: string;
      
      try {
        // 尝试使用虚拟环境
        output = execSync(`"${venvPath}" "${scriptPath}" "${filePath}"`, { encoding: 'utf8' });
      } catch {
        // 如果虚拟环境失败，尝试使用系统Python
        try {
          output = execSync(`python3 "${scriptPath}" "${filePath}"`, { encoding: 'utf8' });
        } catch {
          // 如果系统Python也失败，尝试使用python命令
          output = execSync(`python "${scriptPath}" "${filePath}"`, { encoding: 'utf8' });
        }
      }
      
      // 清理临时文件
      fs.unlinkSync(scriptPath);

      return JSON.parse(output);
    } catch (error) {
      throw new Error(`读取.xls文件失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 读取指定工作表
   * @param filePath 文件路径
   * @param sheetName 工作表名称
   * @returns 工作表数据
   */
  static readExcelSheet(filePath: string, sheetName: string): any[] {
    const sheets = this.readExcelFile(filePath);
    if (!sheets[sheetName]) {
      throw new Error(`工作表不存在: ${sheetName}`);
    }
    return sheets[sheetName];
  }

  /**
   * 获取文件扩展名
   * @param filePath 文件路径
   * @returns 文件扩展名
   */
  static getFileExtension(filePath: string): string {
    return path.extname(filePath).toLowerCase();
  }

  /**
   * 检查文件是否为Excel文件
   * @param filePath 文件路径
   * @returns 是否为Excel文件
   */
  static isExcelFile(filePath: string): boolean {
    const extension = this.getFileExtension(filePath);
    return ['.xls', '.xlsx', '.xlsm'].includes(extension);
  }
}