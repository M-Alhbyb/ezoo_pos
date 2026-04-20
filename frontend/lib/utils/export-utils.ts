import { api } from './websocket-client';

export type ExportFormat = 'csv' | 'xlsx' | 'pdf';

export interface ExportRequest {
  format: ExportFormat;
  start_date: string;
  end_date: string;
}

export interface ExportProgress {
  export_id: string;
  status: 'started' | 'validating' | 'processing' | 'completed' | 'failed';
  progress: number;
  stage?: string;
  download_url?: string;
  error_message?: string;
}

export async function exportReport(
  reportType: 'sales' | 'projects' | 'partners' | 'inventory',
  format: ExportFormat,
  startDate: string,
  endDate: string
): Promise<void> {
  const params = {
    format,
    start_date: startDate,
    end_date: endDate
  };
  
  const response = await api.get(`/reports/${reportType}/export`, {
    params,
    responseType: format === 'pdf' ? 'blob' : 'blob'
  });
  
  const contentDisposition = response.headers['content-disposition'];
  let filename = `${reportType}_report_${startDate}_${endDate}.${format}`;
  
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }
  
  downloadFile(response.data, filename, getMimeType(format));
}

export function downloadFile(
  data: Blob,
  filename: string,
  mimeType: string
): void {
  const blob = new Blob([data], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export function getMimeType(format: ExportFormat): string {
  const mimeTypes: Record<ExportFormat, string> = {
    csv: 'text/csv',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    pdf: 'application/pdf'
  };
  return mimeTypes[format];
}

export function getFileExtension(format: ExportFormat): string {
  return format;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function validateExportFormat(format: string): format is ExportFormat {
  return ['csv', 'xlsx', 'pdf'].includes(format);
}