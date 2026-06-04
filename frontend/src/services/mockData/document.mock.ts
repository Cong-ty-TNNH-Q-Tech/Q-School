import type { Document } from '@/models/document';

let mockDocuments: Document[] = [
  {
    id: 'doc-1',
    filename: 'De_cuong_Sinh_10.pdf',
    status: 'ready',
    format: 'PDF Document',
    size: 2.4 * 1024 * 1024,
    created_at: new Date().toISOString()
  },
  {
    id: 'doc-2',
    filename: 'Sach_giao_khoa_Toan_11.docx',
    status: 'parsing',
    format: 'Word Document',
    size: 15.0 * 1024 * 1024,
    created_at: new Date().toISOString()
  },
  {
    id: 'doc-3',
    filename: 'Hinh_anh_De_thi_thu.jpg',
    status: 'error',
    format: 'Image',
    size: 5.1 * 1024 * 1024,
    created_at: new Date(Date.now() - 86400000).toISOString() // Hôm qua
  }
];

export const getDocumentsMock = async (): Promise<Document[]> => {
  return new Promise(resolve => {
    setTimeout(() => resolve([...mockDocuments]), 500);
  });
};

export const uploadDocumentMock = async (
  file: File, 
  onProgress?: (progress: number) => void
): Promise<Document> => {
  return new Promise((resolve) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20 + 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        // Determine format based on mime type or extension
        let format = 'Document';
        if (file.type.includes('pdf') || file.name.endsWith('.pdf')) format = 'PDF Document';
        else if (file.type.includes('word') || file.name.endsWith('.docx') || file.name.endsWith('.doc')) format = 'Word Document';
        else if (file.type.includes('image') || file.name.endsWith('.jpg') || file.name.endsWith('.png')) format = 'Image';
        
        const newDoc: Document = {
          id: `doc-${Date.now()}`,
          filename: file.name,
          status: 'pending',
          format,
          size: file.size,
          created_at: new Date().toISOString()
        };
        
        mockDocuments = [newDoc, ...mockDocuments];
        if (onProgress) onProgress(100);
        setTimeout(() => resolve(newDoc), 200);
      } else {
        if (onProgress) onProgress(Math.floor(progress));
      }
    }, 200);
  });
};

export const pollDocumentStatusMock = async (id: string): Promise<Document | null> => {
  return new Promise(resolve => {
    setTimeout(() => {
      const docIndex = mockDocuments.findIndex(d => d.id === id);
      if (docIndex === -1) return resolve(null);
      
      const doc = mockDocuments[docIndex];
      
      // Simulate status changes
      if (doc.status === 'pending') {
        mockDocuments[docIndex] = { ...doc, status: 'parsing' };
      } else if (doc.status === 'parsing') {
        // Thay vì random thì cứ set thành ready cho dễ test
        mockDocuments[docIndex] = { ...doc, status: 'ready' };
      }
      
      resolve({ ...mockDocuments[docIndex] });
    }, 300);
  });
};
