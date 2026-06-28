import { useNavigate } from 'react-router-dom';
import { useFlashcardSets } from '@/viewmodels/useFlashcardSets';
import { Button } from '@/components/ui/button';
import { BookOpen, Calendar } from 'lucide-react';

export default function FlashcardSetList() {
  const { sets, isLoading } = useFlashcardSets();
  const navigate = useNavigate();

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Đang tải danh sách bộ thẻ...</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Flashcards</h1>
          <p className="text-gray-500">Ôn tập hiệu quả với thuật toán lặp lại ngắt quãng.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sets.map((set) => (
          <div 
            key={set.id} 
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow cursor-pointer flex flex-col h-full"
            onClick={() => navigate(`/flashcards/${set.id}`)}
          >
            <div className="mb-4">
              <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">{set.title}</h3>
              <p className="text-sm text-gray-500 line-clamp-2">
                Bộ thẻ ôn tập được tạo tự động bởi AI.
              </p>
            </div>
            
            <div className="mt-auto pt-4 border-t border-gray-50 flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-blue-500" />
                <span>{set.card_count || 0} thẻ</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span>{new Date(set.created_at).toLocaleDateString('vi-VN')}</span>
              </div>
            </div>
            
            <Button className="w-full mt-4" variant="default">
              Bắt đầu học
            </Button>
          </div>
        ))}
      </div>
      
      {sets.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900">Chưa có bộ thẻ nào</h3>
          <p className="text-gray-500 mt-1">Tải lên tài liệu để AI tạo bộ thẻ tự động cho bạn.</p>
        </div>
      )}
    </div>
  );
}
