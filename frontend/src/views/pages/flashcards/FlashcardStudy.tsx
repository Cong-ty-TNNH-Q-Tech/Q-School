import { useParams, useNavigate } from 'react-router-dom';
import { useFlashcards } from '@/viewmodels/useFlashcards';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Volume2, Flag, RotateCw, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function FlashcardStudy() {
  const { setId } = useParams<{ setId: string }>();
  const navigate = useNavigate();
  
  const {
    currentCard,
    currentIndex,
    totalCards,
    isFlipped,
    isLoading,
    isSubmitting,
    isCompleted,
    flipCard,
    submitConfidence
  } = useFlashcards(setId || '');

  if (isLoading) {
    return <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-gray-500">Đang tải bộ thẻ...</div>;
  }

  if (isCompleted) {
    return (
      <div className="flex flex-col h-[calc(100vh-4rem)] items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 text-center max-w-md w-full">
          <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Hoàn thành xuất sắc!</h2>
          <p className="text-gray-500 mb-6">Bạn đã hoàn thành phiên ôn tập ngày hôm nay. Hãy tiếp tục duy trì thói quen tốt này nhé!</p>
          <Button onClick={() => navigate('/dashboard/flashcards')} className="w-full">
            Quay lại danh sách
          </Button>
        </div>
      </div>
    );
  }

  if (!currentCard) {
    return <div className="text-center p-8">Không tìm thấy thẻ.</div>;
  }

  // Progress percentage
  const progressValue = totalCards > 0 ? ((currentIndex + 1) / totalCards) * 100 : 0;

  return (
    <div className="flex flex-col h-full min-h-[calc(100vh-4rem)] bg-gray-50/50">
      {/* Header section */}
      <div className="w-full max-w-4xl mx-auto px-4 pt-8 pb-4">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard/flashcards')} className="shrink-0 text-gray-500 hover:text-gray-900">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex-1 flex justify-between items-end">
            <h1 className="text-lg font-medium text-gray-900">Biology 101 - Ecosystems</h1> {/* Could get from set details API, hardcoded to match mockup for now */}
            <span className="text-sm font-medium text-gray-600">Thẻ {currentIndex + 1} / {totalCards}</span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="pl-14"> {/* Align with title */}
          <Progress value={progressValue} className="h-2 bg-gray-200" />
        </div>
      </div>

      {/* Main Card Area */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        
        {/* The Card Container with 3D perspective */}
        <div 
          className="relative w-full max-w-3xl aspect-[16/9] sm:aspect-[21/9] cursor-pointer group"
          style={{ perspective: '1000px' }}
          onClick={() => !isFlipped && flipCard()}
        >
          {/* Card Inner wrapper for flipping */}
          <div 
            className={cn(
              "w-full h-full relative transition-transform duration-500 ease-in-out",
              isFlipped ? "[transform:rotateY(180deg)]" : ""
            )}
            style={{ transformStyle: 'preserve-3d' }}
          >
            
            {/* FRONT OF CARD */}
            <div 
              className={cn(
                "absolute w-full h-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col",
                "backface-hidden"
              )}
              style={{ backfaceVisibility: 'hidden' }}
            >
              <div className="flex justify-between items-start">
                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-gray-700 h-8 w-8" onClick={(e) => { e.stopPropagation(); /* Play sound */ }}>
                  <Volume2 className="w-5 h-5" />
                </Button>
                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-gray-700 h-8 w-8" onClick={(e) => { e.stopPropagation(); /* Flag issue */ }}>
                  <Flag className="w-5 h-5" />
                </Button>
              </div>
              
              <div className="flex-1 flex items-center justify-center">
                <h2 className="text-3xl md:text-4xl text-center font-medium text-gray-900 px-4">
                  {currentCard.front_text}
                </h2>
              </div>
              
              <div className="flex justify-center text-gray-400 items-center gap-2 pb-2 opacity-60 group-hover:opacity-100 transition-opacity">
                <span className="text-xs font-medium tracking-wider uppercase">Nhấn để lật</span>
                <RotateCw className="w-3.5 h-3.5" />
              </div>
            </div>

            {/* BACK OF CARD */}
            <div 
              className={cn(
                "absolute w-full h-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col",
                "backface-hidden"
              )}
              style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            >
              <div className="flex justify-between items-start">
                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-gray-700 h-8 w-8" onClick={(e) => { e.stopPropagation(); /* Play sound */ }}>
                  <Volume2 className="w-5 h-5" />
                </Button>
                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-gray-700 h-8 w-8" onClick={(e) => { e.stopPropagation(); /* Flag issue */ }}>
                  <Flag className="w-5 h-5" />
                </Button>
              </div>
              
              <div className="flex-1 flex flex-col items-center justify-center gap-6">
                {/* Optional: Show front text smaller on top */}
                <div className="text-sm text-gray-400 pb-4 border-b border-gray-100 px-8 text-center w-full max-w-md">
                  {currentCard.front_text}
                </div>
                
                <h2 className="text-2xl md:text-3xl text-center text-gray-900 px-4 whitespace-pre-wrap">
                  {currentCard.back_text}
                </h2>
              </div>
            </div>

          </div>
        </div>

        {/* Action Area below the card */}
        <div className="mt-12 h-16 w-full max-w-3xl flex justify-center items-center">
          {!isFlipped ? (
            <Button 
              className="px-8 h-12 rounded-lg text-base shadow-sm hover:shadow-md transition-shadow bg-[#5441E7] hover:bg-[#5441E7]/90 text-white flex items-center gap-2"
              onClick={flipCard}
            >
              <span>Lật thẻ xem đáp án</span>
              <RotateCw className="w-4 h-4" />
            </Button>
          ) : (
            <div className="flex flex-col items-center w-full animate-in fade-in slide-in-from-bottom-4 duration-300">
              <span className="text-sm text-gray-500 mb-3 font-medium">Bạn có nhớ thẻ này không?</span>
              <div className="flex flex-wrap justify-center gap-2 sm:gap-3 w-full">
                <Button 
                  disabled={isSubmitting}
                  onClick={() => submitConfidence(1)} 
                  variant="confidence1" 
                  className="flex-1 max-w-[140px] h-12 font-semibold"
                >
                  1. Quên sạch
                </Button>
                <Button 
                  disabled={isSubmitting}
                  onClick={() => submitConfidence(2)} 
                  variant="confidence2" 
                  className="flex-1 max-w-[140px] h-12 font-semibold"
                >
                  2. Khó nhớ
                </Button>
                <Button 
                  disabled={isSubmitting}
                  onClick={() => submitConfidence(3)} 
                  variant="confidence3" 
                  className="flex-1 max-w-[140px] h-12 font-semibold"
                >
                  3. Bình thường
                </Button>
                <Button 
                  disabled={isSubmitting}
                  onClick={() => submitConfidence(4)} 
                  variant="confidence4" 
                  className="flex-1 max-w-[140px] h-12 font-semibold"
                >
                  4. Khá tốt
                </Button>
                <Button 
                  disabled={isSubmitting}
                  onClick={() => submitConfidence(5)} 
                  variant="confidence5" 
                  className="flex-1 max-w-[140px] h-12 font-semibold"
                >
                  5. Rất thuộc
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
