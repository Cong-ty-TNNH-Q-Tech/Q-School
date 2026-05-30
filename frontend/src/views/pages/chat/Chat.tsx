import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const MOCK_MESSAGES: Message[] = [
  { id: '1', role: 'assistant', content: 'Xin chào! Tôi là trợ lý AI của Q-School. Tôi có thể giúp bạn giải bài tập, ôn thi, hoặc giải thích kiến thức. Bạn cần giúp gì?' },
]

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES)
  const [input, setInput] = useState('')

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input }
    const aiMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: 'Đây là phản hồi mẫu. Khi Backend sẵn sàng, phản hồi sẽ được stream qua SSE từ mô hình AI.',
    }

    setMessages((prev) => [...prev, userMsg, aiMsg])
    setInput('')
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4">
        <h2 className="text-2xl font-bold tracking-tight">AI Chat</h2>
        <p className="text-muted-foreground">Trợ lý AI hỗ trợ học tập</p>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Cuộc trò chuyện mới</CardTitle>
        </CardHeader>
        <Separator />
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <Avatar className="h-8 w-8 shrink-0">
                <AvatarFallback className={msg.role === 'assistant' ? 'bg-primary text-primary-foreground' : ''}>
                  {msg.role === 'assistant' ? 'AI' : 'U'}
                </AvatarFallback>
              </Avatar>
              <div
                className={`max-w-[75%] rounded-lg px-4 py-2 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </CardContent>
        <Separator />
        <div className="p-4">
          <form onSubmit={handleSend} className="flex gap-2">
            <Input
              id="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập câu hỏi..."
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim()}>
              Gửi
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
