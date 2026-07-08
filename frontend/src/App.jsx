import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import NeuralBackground from './components/NeuralBackground'
import ProtectedRoute from './components/ProtectedRoute'

import Home from './pages/Home'
import MachineLearning from './pages/MachineLearning'
import DeepLearning from './pages/DeepLearning'
import AIAgent from './pages/AIAgent'
import Automation from './pages/Automation'
import ProjectDetail from './pages/ProjectDetail'
import About from './pages/About'
// import Contact from './pages/Contact' // hidden for now
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import DashboardNewProject from './pages/DashboardNewProject'
import DashboardEditProject from './pages/DashboardEditProject'
import DashboardMessages from './pages/DashboardMessages'
import Profile from './pages/Profile'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <NeuralBackground />
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/machine-learning" element={<MachineLearning />} />
          <Route path="/machine-learning/:method" element={<MachineLearning />} />

          <Route path="/deep-learning" element={<DeepLearning />} />
          <Route path="/deep-learning/:method" element={<DeepLearning />} />

          <Route path="/ai-agent" element={<AIAgent />} />
          <Route path="/ai-agent/:method" element={<AIAgent />} />

          <Route path="/automation" element={<Automation />} />
          <Route path="/automation/:method" element={<Automation />} />

          <Route path="/projects/:slug" element={<ProjectDetail />} />

          <Route path="/about" element={<About />} />
          {/* Contact page hidden for now — restore this route to bring it back */}
          {/* <Route path="/contact" element={<Contact />} /> */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/dashboard/new" element={<ProtectedRoute><DashboardNewProject /></ProtectedRoute>} />
          <Route path="/dashboard/edit/:id" element={<ProtectedRoute><DashboardEditProject /></ProtectedRoute>} />
          <Route path="/dashboard/messages" element={<ProtectedRoute><DashboardMessages /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
