export const ML_METHODS = [
  'Linear Regression',
  'Logistic Regression',
  'Decision Tree',
  'Random Forest',
  'Support Vector Machine',
  'K-Nearest Neighbors',
  'Naive Bayes',
  'K-Means Clustering',
  'Principal Component Analysis',
  'Gradient Boosting / XGBoost',
]

export const DL_METHODS = [
  'Artificial Neural Network',
  'Convolutional Neural Network',
  'Recurrent Neural Network',
  'LSTM / GRU',
  'Transformers',
  'Autoencoders',
  'Transfer Learning',
]

export const AGENT_TYPES = [
  'Personal AI Assistant',
  'Research Agent',
  'Resume Screening Agent',
  'Data Analysis Agent',
  'Customer Support Agent',
  'Document Q&A Agent',
  'RAG-based Agent',
  'Multi-Agent Workflow',
]

export const AUTOMATION_TYPES = [
  'Report Automation',
  'Email Automation',
  'Data Pipeline Automation',
  'Excel / Power BI Automation',
  'Document Processing Automation',
  'Web Scraping Automation',
  'Workflow Automation',
  'HR / Recruitment Automation',
  'Customer Support Automation',
]

export const NAV_SECTIONS = [
  { label: 'Machine Learning', path: '/machine-learning', slug: 'machine-learning', items: ML_METHODS, icon: 'BrainCircuit' },
  { label: 'Deep Learning', path: '/deep-learning', slug: 'deep-learning', items: DL_METHODS, icon: 'Network' },
  { label: 'AI Agent', path: '/ai-agent', slug: 'ai-agent', items: AGENT_TYPES, icon: 'Bot' },
  { label: 'Automation', path: '/automation', slug: 'automation', items: AUTOMATION_TYPES, icon: 'Workflow' },
]
