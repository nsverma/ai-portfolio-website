import CategoryPage from './CategoryPage'
import { AUTOMATION_TYPES } from '../data/menuData'

export default function Automation() {
  return (
    <CategoryPage
      categorySlug="automation"
      title="Automation"
      description="Industry automation projects that replace manual, repetitive work with reliable, scheduled pipelines."
      icon="Workflow"
      items={AUTOMATION_TYPES}
    />
  )
}
