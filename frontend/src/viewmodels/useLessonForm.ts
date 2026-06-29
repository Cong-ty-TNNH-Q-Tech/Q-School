import { useState, useEffect, useMemo } from 'react'
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

const DEFAULT_SECTION = { title: '', content: '', duration_minutes: 0 }

export function useLessonForm(lessonId?: string): UseLessonFormReturn {
  const isEditMode = Boolean(lessonId)
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const { selectedLesson, fetchLessonDetail, createLesson, updateLesson, isLoading, error } = useLessons()

  // Load data for edit mode
  useEffect(() => {
    if (isEditMode && lessonId) {
      fetchLessonDetail(lessonId)
    }
  }, [isEditMode, lessonId, fetchLessonDetail])

  // Derive initial values from selectedLesson (avoids setState inside effect)
  const initialValues = useMemo(() => {
    if (isEditMode && selectedLesson) {
      const content = selectedLesson.content
      return {
        title: selectedLesson.title,
        subject: selectedLesson.subject || '',
        gradeLevel: selectedLesson.grade_level || '',
        objectives: content?.objectives?.length ? content.objectives : [''],
        sections: content?.sections?.length ? content.sections : [DEFAULT_SECTION],
        materials: content?.materials?.length ? content.materials : [''],
        homework: content?.homework || '',
      }
    }
    return {
      title: '',
      subject: '',
      gradeLevel: '',
      objectives: [''],
      sections: [DEFAULT_SECTION],
      materials: [''],
      homework: '',
    }
  }, [isEditMode, selectedLesson])

  // Form State
  const [title, setTitle] = useState(initialValues.title)
  const [subject, setSubject] = useState(initialValues.subject)
  const [gradeLevel, setGradeLevel] = useState(initialValues.gradeLevel)
  const [objectives, setObjectives] = useState<string[]>(initialValues.objectives)
  const [sections, setSections] = useState<Required<LessonContent>['sections']>(initialValues.sections)
  const [materials, setMaterials] = useState<string[]>(initialValues.materials)
  const [homework, setHomework] = useState(initialValues.homework)

  // Sync form state when initialValues change (lesson data loaded async)
  useEffect(() => {
    setTitle(initialValues.title)
    setSubject(initialValues.subject)
    setGradeLevel(initialValues.gradeLevel)
    setObjectives(initialValues.objectives)
    setSections(initialValues.sections)
    setMaterials(initialValues.materials)
    setHomework(initialValues.homework)
  // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional sync from derived initialValues
  }, [initialValues])

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
    } catch {
      // Error is already handled by the store via error state
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
