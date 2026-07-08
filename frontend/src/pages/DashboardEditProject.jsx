import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import DashboardLayout from '../components/DashboardLayout'
import ProjectForm from '../components/ProjectForm'
import Loader from '../components/Loader'
import { getCategories, getProjectBySlug, updateProject } from '../services/projectService'

export default function DashboardEditProject() {
  const { id } = useParams()
  const [categories, setCategories] = useState([])
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([getCategories(), getProjectBySlug(id)])
      .then(([cats, proj]) => { setCategories(cats); setProject(proj) })
      .finally(() => setLoading(false))
  }, [id])

  const handleSubmit = async (payload) => {
    await updateProject(project.id, payload)
    navigate('/dashboard')
  }

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold text-white mb-6">Edit Project</h1>
      {loading ? (
        <Loader />
      ) : (
        <ProjectForm categories={categories} initialData={project} onSubmit={handleSubmit} submitLabel="Save Changes" />
      )}
    </DashboardLayout>
  )
}
