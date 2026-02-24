import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import Dashboard from "./pages/Dashboard";
import DrugBrowser from "./pages/DrugBrowser";
import DrugDetail from "./pages/DrugDetail";
import TargetExplorer from "./pages/TargetExplorer";
import TargetDetail from "./pages/TargetDetail";
import PathwayBrowser from "./pages/PathwayBrowser";
import Predictions from "./pages/Predictions";
import Simulation from "./pages/Simulation";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/drugs" element={<DrugBrowser />} />
            <Route path="/drugs/:id" element={<DrugDetail />} />
            <Route path="/targets" element={<TargetExplorer />} />
            <Route path="/targets/:id" element={<TargetDetail />} />
            <Route path="/pathways" element={<PathwayBrowser />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/simulation" element={<Simulation />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
