import CategoryPage from './CategoryPage'
import { AGENT_TYPES } from '../data/menuData'

export default function AIAgent() {
  return (
    <CategoryPage
      categorySlug="ai-agent"
      title="AI Agent"
      description="LLM-powered agents — from single-purpose assistants to multi-agent orchestration — solving real workflow problems."
      icon="Bot"
      items={AGENT_TYPES}
    />
  )
}
