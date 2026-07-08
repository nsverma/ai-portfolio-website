import CategoryPage from './CategoryPage'
import { ML_METHODS } from '../data/menuData'

export default function MachineLearning() {
  return (
    <CategoryPage
      categorySlug="machine-learning"
      title="Machine Learning"
      description="Classical ML algorithms — regression, classification, and clustering — applied to real business problems, each with a baseline-to-tuned model comparison."
      icon="BrainCircuit"
      items={ML_METHODS}
    />
  )
}
