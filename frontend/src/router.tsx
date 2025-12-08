import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Model from "./pages/models/model"
import Dataset from "./pages/datasets/dataset"
import Experiment from "./pages/experiments/experiment"
import Jobs from "./pages/jobs"
import JobsTrain from "./pages/jobs/train"
import JobsInfere from "./pages/jobs/infere"
import InferenceApps from "./pages/inference"
import Explore from "./pages/explore"
import Evaluate from "./pages/evaluate"
import EvaluateSubmit from "./pages/evaluate/submit"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/models/:owner/:name" element={<Model />} />
        <Route path="/datasets/:owner/:name" element={<Dataset />} />
        <Route path="/experiments/:id" element={<Experiment />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/train" element={<JobsTrain />} />
        <Route path="/jobs/infere" element={<JobsInfere />} />
        <Route path="/evaluate" element={<Evaluate />} />
        <Route path="/evaluate/submit" element={<EvaluateSubmit />} />
        <Route path="/inference" element={<InferenceApps />} />
        {/* <Route path="/experiments" element={<Experiments />} /> */}
      </Route>
    </Routes>
  )
}
