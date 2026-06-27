import type { SSEChunk } from '@/models/chat';

/**
 * Giả lập luồng SSE từ backend (Mock)
 * Sử dụng AsyncGenerator + setTimeout để tạo hiệu ứng gõ phím
 */
export async function* streamMockChatResponse(content: string): AsyncGenerator<SSEChunk, void, unknown> {
  // Phản hồi giả lập dựa trên tin nhắn user hoặc mặc định
  let responseText = "Dưới đây là các bước để giải bài toán này:\n\n1. **Phân tích đề bài**: Xác định các hệ số a, b, c của phương trình `ax^2 + bx + c = 0`.\n2. Tính Delta (Δ) theo công thức: `Δ = b^2 - 4ac`\n\n> Lưu ý: Nếu Δ < 0, phương trình vô nghiệm trên tập số thực.";
  
  const lowerContent = content.toLowerCase();
  if (lowerContent.includes("lớp học đảo ngược")) {
    responseText = "Lớp học đảo ngược (Flipped Classroom) là mô hình học tập mà học sinh sẽ tự tìm hiểu bài mới ở nhà qua video hoặc tài liệu, sau đó lên lớp để làm bài tập, thảo luận và tương tác với giáo viên.";
  } else if (lowerContent.includes("phá băng")) {
    responseText = "Trò chơi phá băng (Icebreaker) giúp tạo không khí thoải mái cho lớp học.\n\nMột số trò chơi phổ biến:\n- **Hai sự thật, một lời nói dối**\n- **Đuổi hình bắt chữ**\n- **Nối từ**";
  } else if (lowerContent.includes("kiểm tra 15p")) {
    responseText = "Dưới đây là một số câu hỏi trắc nghiệm 15 phút về môn Lịch sử:\n1. Ai là người đọc Tuyên ngôn Độc lập năm 1945?\n2. Chiến dịch Điện Biên Phủ diễn ra vào năm nào?\n3. Vị vua cuối cùng của triều Nguyễn là ai?";
  } else if (lowerContent.includes("pythagoras")) {
    responseText = "Định lý Pythagoras phát biểu rằng:\n\nTrong một tam giác vuông, bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông.\nCông thức: `a^2 + b^2 = c^2` (với c là cạnh huyền).";
  }

  // Tách text thành các token nhỏ để stream
  const tokens = responseText.split(/(?<=\s)|(?=[.,;!?:])/);
  
  // Trễ 500ms ban đầu để giả lập API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  for (let i = 0; i < tokens.length; i++) {
    // Delay ngẫu nhiên để tạo hiệu ứng gõ phím (20ms - 60ms)
    const delay = Math.random() * 40 + 20;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    yield {
      chunk: tokens[i],
      is_final: i === tokens.length - 1
    };
  }
}
