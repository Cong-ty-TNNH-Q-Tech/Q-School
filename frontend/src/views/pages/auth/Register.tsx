import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { GraduationCap, Loader2, ArrowRight } from 'lucide-react'

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.')
      return
    }

    setLoading(true)
    try {
      // TODO: Thay bằng apiClient.post('/auth/register') khi Backend sẵn sàng
      await new Promise((resolve) => setTimeout(resolve, 1000))
      navigate('/login')
    } catch {
      setError('Đăng ký thất bại. Vui lòng thử lại.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-950 py-10">
      {/* Dynamic Background */}
      <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-600/20 blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-teal-600/20 blur-[150px] animate-pulse" style={{ animationDelay: '2s' }} />
      <div className="absolute top-[30%] left-[20%] w-[30%] h-[30%] rounded-full bg-cyan-500/20 blur-[100px] animate-pulse" style={{ animationDelay: '4s' }} />
      
      {/* Content */}
      <div className="relative z-10 w-full max-w-md px-4 sm:px-0">
        <div className="mb-6 flex flex-col items-center justify-center space-y-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 shadow-xl shadow-emerald-500/30">
            <GraduationCap className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Tạo tài khoản
          </h1>
          <p className="text-sm text-slate-400">
            Trở thành học viên của Q-School AI
          </p>
        </div>

        <div className="backdrop-blur-xl bg-white/5 border border-white/10 shadow-2xl rounded-3xl p-8 transition-all hover:bg-white/[0.07]">
          <form onSubmit={handleRegister} className="space-y-5">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName" className="text-slate-300 ml-1">Họ và tên</Label>
                <Input
                  id="fullName"
                  placeholder="Nguyễn Văn A"
                  type="text"
                  autoCapitalize="words"
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={loading}
                  required
                  className="bg-slate-900/50 border-white/10 text-white placeholder:text-slate-500 focus-visible:ring-emerald-500 h-11 rounded-xl"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-300 ml-1">Email</Label>
                <Input
                  id="email"
                  placeholder="name@example.com"
                  type="email"
                  autoCapitalize="none"
                  autoComplete="email"
                  autoCorrect="off"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  required
                  className="bg-slate-900/50 border-white/10 text-white placeholder:text-slate-500 focus-visible:ring-emerald-500 h-11 rounded-xl"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-slate-300 ml-1">Mật khẩu</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    required
                    className="bg-slate-900/50 border-white/10 text-white focus-visible:ring-emerald-500 h-11 rounded-xl"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-slate-300 ml-1">Xác nhận</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    required
                    className="bg-slate-900/50 border-white/10 text-white focus-visible:ring-emerald-500 h-11 rounded-xl"
                  />
                </div>
              </div>
            </div>
            
            {error && (
              <div className="rounded-lg bg-red-500/10 p-3 border border-red-500/20 text-sm font-medium text-red-400 text-center">
                {error}
              </div>
            )}
            
            <Button 
              disabled={loading} 
              className="w-full h-12 text-base font-semibold rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white shadow-lg shadow-emerald-500/25 transition-all group mt-2"
            >
              {loading ? (
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              ) : (
                <>
                  Đăng ký
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </Button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-400">
              Đã có tài khoản?{" "}
              <Link
                to="/login"
                className="font-medium text-emerald-400 hover:text-emerald-300 hover:underline underline-offset-4 transition-all"
              >
                Đăng nhập
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
