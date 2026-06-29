import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLessons } from './useLessons'
import { useAuthStore } from '@/stores/useAuthStore'
import type { LessonContent } from '@/models'

export interface UseLessonFormReturn {
  // Form state
  title: string
  setTitle: (v: string) => void
  subject: string
  setSubject: (v: string) => void
  gradeLevel: string
  setGradeLevel: (v: string) => void
  objectives: string[]
  sections: Required<LessonContent>['sections']
  materials: string[]
  homework: string
  setHomework: (v: string) => void

  // Dynamic list handlers
  handleObjectiveChange: (index: number, value: string) => void
  addObjective: () => void
  removeObjective: (index: number) => void

  handleSectionChange: (index: number, field: keyof Required<LessonContent>['sections'][0], value: string | number) => void
  addSection: () => void
  removeSection: (index: number) => void

  handleMaterialChange: (index: number, value: string) => void
  addMaterial: () => void
  removeMaterial: (index: number) => void

  // Submit
  handleSubmit: (e: React.FormEvent) => Promise<void>
  isLoading: boolean
  error: string | null
}

export function useLessonForm(lessonId?: string): UseLessonFormReturn {
  const isEditMode = Boolean(lessonId)
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const { selectedLesson, fetchLessonDetail, createLesson, updateLesson, isLoading, error } = useLessons()

  // Form State
  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [gradeLevel, setGradeLevel] = useState('')
  const [objectives, setObjectives] = useState<string[]>([''])
  const [sections, setSections] = useState<Required<LessonContent>['sections']>([
    { title: '', content: '', duration_minutes: 0 }
  ])
  const [materials, setMaterials] = useState<string[]>([''])
  const [homework, setHomework] = useState('')

  // Load data for edit mode
  useEffect(() => {
    if (isEditMode && lessonId) {
      fetchLessonDetail(lessonId)
    }
  }, [isEditMode, lessonId, fetchLessonDetail])

  // Populate form state when selectedLesson is available
  useEffect(() => {
    if (isEditMode && selectedLesson) {
      setTitle(selectedLesson.title)
      setSubject(selectedLesson.subject || '')
      setGradeLevel(selectedLesson.grade_level || '')
      
      const content = selectedLesson.content
      if (content) {
        setObjectives(content.objectives?.length ? content.objectives : [''])
        setSections(content.sections?.length ? content.sections : [{ title: '', content: '', duration_minutes: 0 }])
        setMaterials(content.materials?.length ? content.materials : [''])
        setHomework(content.homework || '')
      }
    }
  }, [isEditMode, selectedLesson])

  // Handlers for dynamic lists
  const handleObjectiveChange = (index: number, value: string) => {
    const newObjs = [...objectives]
    newObjs[index] = value
    setObjectives(newObjs)
  }
  
  const addObjective = () => setObjectives([...objectives, ''])
  const removeObjective = (index: number) => {
    if (objectives.length > 1) {
      setObjectives(objectives.filter((_, i) => i !== index))
    }
  }

  const handleMaterialChange = (index: number, value: string) => {
    const newMats = [...materials]
    newMats[index] = value
    setMaterials(newMats)
  }
  
  const addMaterial = () => setMaterials([...materials, ''])
  const removeMaterial = (index: number) => {
    if (materials.length > 1) {
      setMaterials(materials.filter((_, i) => i !== index))
    }
  }

  const handleSectionChange = (index: number, field: keyof Required<LessonContent>['sections'][0], value: string | number) => {
    const newSections = [...sections]
    newSections[index] = { ...newSections[index], [field]: value }
    setSections(newSections)
  }
  
  const addSection = () => setSections([...sections, { title: '', content: '', duration_minutes: 0 }])
  const removeSection = (index: number) => {
    if (sections.length > 1) {
      setSections(sections.filter((_, i) => i !== index))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Clean up empty fields
    const cleanObjectives = objectives.filter(o => o.trim() !== '')
    const cleanMaterials = materials.filter(m => m.trim() !== '')
    const cleanSections = sections.filter(s => s.title.trim() !== '' || s.content.trim() !== '')

    const payload = {
      title,
      subject: subject || undefined,
      grade_level: gradeLevel || undefined,
      content: {
        objectives: cleanObjectives.length > 0 ? cleanObjectives : undefined,
        sections: cleanSections.length > 0 ? cleanSections : undefined,
        materials: cleanMaterials.length > 0 ? cleanMaterials : undefined,
        homework: homework.trim() !== '' ? homework : undefined
      }
    }

    try {
      if (isEditMode && lessonId) {
        await updateLesson(lessonId, payload)
        navigate(`/lessons/${lessonId}`)
      } else if (user) {
        await createLesson(payload, user.id)
        navigate('/lessons')
      }
    } catch (err) {
      // Error is already handled by the store, no need to console.error
      // Component can read the `error` state from this hook
    }
  }

  return {
    title, setTitle,
    subject, setSubject,
    gradeLevel, setGradeLevel,
    objectives, sections, materials, homework, setHomework,
    handleObjectiveChange, addObjective, removeObjective,
    handleSectionChange, addSection, removeSection,
    handleMaterialChange, addMaterial, removeMaterial,
    handleSubmit,
    isLoading, error
  }
}
