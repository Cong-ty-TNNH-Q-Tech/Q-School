import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ClassFormDialog from './ClassFormDialog'
import { useClasses } from '@/viewmodels/useClasses'
import { useAuthStore } from '@/stores/useAuthStore'

vi.mock('@/viewmodels/useClasses', () => ({
  useClasses: vi.fn(),
}))

vi.mock('@/stores/useAuthStore', () => ({
  useAuthStore: vi.fn(),
}))

describe('ClassFormDialog', () => {
  const mockCreateClass = vi.fn()
  const mockUpdateClass = vi.fn()
  const mockOnOpenChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useClasses).mockReturnValue({
      createClass: mockCreateClass,
      updateClass: mockUpdateClass,
      isLoading: false,
    } as any)
    
    // Simulate useAuthStore behavior
    vi.mocked(useAuthStore).mockImplementation((selector: any) => 
      selector({ user: { id: 'user-1' } })
    )
  })

  it('renders create form correctly', () => {
    render(<ClassFormDialog open={true} onOpenChange={mockOnOpenChange} />)
    expect(screen.getByText('Tạo lớp học mới')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Tạo mới' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Tạo mới' })).toBeDisabled() // Because name is empty
  })

  it('populates data in edit mode', () => {
    const classData = { 
      id: 'c1', name: 'Math 101', grade_level: '10', subject: 'Math', 
      created_at: '', updated_at: '', teacher_id: 'u1', student_count: 0 
    }
    render(<ClassFormDialog open={true} onOpenChange={mockOnOpenChange} classData={classData} />)
    expect(screen.getByText('Cập nhật lớp học')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Math 101')).toBeInTheDocument()
    expect(screen.getByDisplayValue('10')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cập nhật' })).not.toBeDisabled()
  })

  it('calls createClass when submitted', async () => {
    render(<ClassFormDialog open={true} onOpenChange={mockOnOpenChange} />)
    
    // Type into inputs
    const nameInput = screen.getByLabelText(/Tên lớp/i)
    fireEvent.change(nameInput, { target: { value: 'New Class' } })
    
    const submitBtn = screen.getByRole('button', { name: 'Tạo mới' })
    expect(submitBtn).not.toBeDisabled()
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(mockCreateClass).toHaveBeenCalledWith(
        { name: 'New Class', grade_level: '', subject: '' },
        'user-1'
      )
      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })
  })

  it('calls updateClass when submitted in edit mode', async () => {
    const classData = { 
      id: 'c1', name: 'Math 101', grade_level: '10', subject: 'Math', 
      created_at: '', updated_at: '', teacher_id: 'u1', student_count: 0 
    }
    render(<ClassFormDialog open={true} onOpenChange={mockOnOpenChange} classData={classData} />)
    
    const nameInput = screen.getByLabelText(/Tên lớp/i)
    fireEvent.change(nameInput, { target: { value: 'Advanced Math' } })
    
    const submitBtn = screen.getByRole('button', { name: 'Cập nhật' })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(mockUpdateClass).toHaveBeenCalledWith(
        'c1',
        { name: 'Advanced Math', grade_level: '10', subject: 'Math' }
      )
      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })
  })
})
