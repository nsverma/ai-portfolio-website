import CategoryPage from './CategoryPage'
import { DL_METHODS } from '../data/menuData'

export default function DeepLearning() {
  return (
    <CategoryPage
      categorySlug="deep-learning"
      title="Deep Learning"
      description="Neural network architectures — from feedforward nets to transformers — for vision, language, and sequence problems."
      icon="Network"
      items={DL_METHODS}
    />
  )
}
