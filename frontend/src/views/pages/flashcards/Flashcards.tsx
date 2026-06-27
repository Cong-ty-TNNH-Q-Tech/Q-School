import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const MOCK_DECKS = [
  { id: '1', title: 'Từ vựng Toán học', cardCount: 50, mastered: 32, color: 'bg-blue-500/10 border-blue-500/20' },
  { id: '2', title: 'Công thức Vật Lý', cardCount: 35, mastered: 20, color: 'bg-green-500/10 border-green-500/20' },
  { id: '3', title: 'Thuật ngữ Lập Trình', cardCount: 60, mastered: 45, color: 'bg-purple-500/10 border-purple-500/20' },
]

export default function Flashcards() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Flashcards</h2>
          <p className="text-muted-foreground">
            Ôn tập kiến thức với thẻ ghi nhớ
          </p>
        </div>
        <Button>Tạo bộ thẻ mới</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {MOCK_DECKS.map((deck) => {
          const progress = Math.round((deck.mastered / deck.cardCount) * 100)
          return (
            <Card key={deck.id} className={deck.color}>
              <CardHeader>
                <CardTitle className="text-lg">{deck.title}</CardTitle>
                <CardDescription>{deck.cardCount} thẻ</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Tiến độ</span>
                    <Badge variant="secondary">{progress}%</Badge>
                  </div>
                  <div className="h-2 w-full rounded-full bg-secondary">
                    <div
                      className="h-2 rounded-full bg-primary transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {deck.mastered}/{deck.cardCount} thẻ đã thuộc
                  </p>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full">
                  Ôn tập
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
