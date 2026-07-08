import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../components/DashboardLayout'
import ProjectForm from '../components/ProjectForm'
import { createProject, getCategories } from '../services/projectService'

export default function DashboardNewProject() {
  const [categories, setCategories] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    getCategories().then(setCategories)
  }, [])

  const handleSubmit = async (payload) => {
    await createProject(payload)
    navigate('/dashboard')
  }

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold text-white mb-6">Add New Project</h1>
      <ProjectForm categories={categories} onSubmit={handleSubmit} submitLabel="Create Project" />
    </DashboardLayout>
  )
}
