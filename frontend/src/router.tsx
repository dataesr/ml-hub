import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Models from "./pages/models"
import Model from "./pages/models/model"
import Datasets from "./pages/datasets"
import Dataset from "./pages/datasets/dataset"
import Jobs from "./pages/jobs"
import JobsSubmit from "./pages/jobs/submit"
import Experiments from "./pages/experiments"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/models" element={<Models />} />
        <Route path="/models/:owner/:name" element={<Model />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/datasets/:owner/:name" element={<Dataset />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/submit" element={<JobsSubmit />} />
        <Route path="/experiments" element={<Experiments />} />
      </Route>
    </Routes>
  )
}
