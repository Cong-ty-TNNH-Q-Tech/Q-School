export type DocumentStatus = 'pending' | 'parsing' | 'ready' | 'error';

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  size?: number; // Size in bytes
  format?: string; // e.g., "PDF Document", "Word Document", "Image"
  created_at?: string; // Date string
}
