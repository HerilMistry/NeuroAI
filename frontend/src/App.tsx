import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { DrugExplorer } from './pages/DrugExplorer'
import { DrugDetail } from './pages/DrugDetail'
import { Pathways } from './pages/Pathways'
import { Simulation } from './pages/Simulation'

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/drugs" element={<DrugExplorer />} />
                <Route path="/drugs/:id" element={<DrugDetail />} />
                <Route path="/pathways" element={<Pathways />} />
                <Route path="/simulation" element={<Simulation />} />
            </Routes>
        </Layout>
    )
}

export default App
