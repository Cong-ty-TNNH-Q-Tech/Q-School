import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

const MOCK_QUESTIONS = [
  {
    id: '1',
    content: 'Giới hạn của hàm số f(x) = (x² - 1)/(x - 1) khi x tiến về 1 là bao nhiêu?',
    options: ['0', '1', '2', 'Không tồn tại'],
  },
  {
    id: '2',
    content: 'Hàm số f(x) = |x| liên tục tại x = 0?',
    options: ['Đúng', 'Sai', 'Không xác định', 'Tùy điều kiện'],
  },
  {
    id: '3',
    content: 'Đạo hàm của hàm f(x) = x³ là gì?',
    options: ['x²', '2x²', '3x²', '3x'],
  },
]

export default function QuizTake() {
  const { id } = useParams<{ id: string }>()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})

  const question = MOCK_QUESTIONS[currentQuestion]

  const handleSelectAnswer = (optionIndex: number) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [question.id]: optionIndex,
    }))
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          <Link to="/quizzes" className="hover:underline">Bài kiểm tra</Link>
          <span>/</span>
          <Link to={`/quizzes/${id}`} className="hover:underline">Kiểm tra Giới hạn</Link>
          <span>/</span>
          <span>Làm bài</span>
        </div>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Kiểm tra Giới hạn</h2>
          <Badge variant="outline">
            Câu {currentQuestion + 1} / {MOCK_QUESTIONS.length}
          </Badge>
        </div>
      </div>

      {/* Progress */}
      <div className="h-2 w-full rounded-full bg-secondary">
        <div
          className="h-2 rounded-full bg-primary transition-all"
          style={{ width: `${((currentQuestion + 1) / MOCK_QUESTIONS.length) * 100}%` }}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg leading-relaxed">
            Câu {currentQuestion + 1}: {question.content}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {question.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleSelectAnswer(index)}
                className={`w-full rounded-lg border p-4 text-left text-sm transition-colors ${
                  selectedAnswers[question.id] === index
                    ? 'border-primary bg-primary/5 font-medium'
                    : 'border-border hover:bg-accent'
                }`}
              >
                <span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full border text-xs font-medium">
                  {String.fromCharCode(65 + index)}
                </span>
                {option}
              </button>
            ))}
          </div>
        </CardContent>
        <Separator />
        <CardFooter className="justify-between pt-4">
          <Button
            variant="outline"
            onClick={() => setCurrentQuestion((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestion === 0}
          >
            Câu trước
          </Button>
          {currentQuestion < MOCK_QUESTIONS.length - 1 ? (
            <Button
              onClick={() => setCurrentQuestion((prev) => Math.min(MOCK_QUESTIONS.length - 1, prev + 1))}
            >
              Câu tiếp
            </Button>
          ) : (
            <Button>Nộp bài</Button>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
