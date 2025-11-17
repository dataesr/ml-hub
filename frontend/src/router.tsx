import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Model from "./pages/models/model"
import Dataset from "./pages/datasets/dataset"
import Jobs from "./pages/jobs"
import JobsSubmit from "./pages/jobs/submit"
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
        {/* <Route path="/models" element={<Models />} /> */}
        <Route path="/models/:owner/:name" element={<Model />} />
        {/* <Route path="/datasets" element={<Datasets />} /> */}
        <Route path="/datasets/:owner/:name" element={<Dataset />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/submit" element={<JobsSubmit />} />
        <Route path="/evaluate" element={<Evaluate />} />
        <Route path="/evaluate/submit" element={<EvaluateSubmit />} />
        <Route path="/inference" element={<InferenceApps />} />
        {/* <Route path="/experiments" element={<Experiments />} /> */}
      </Route>
    </Routes>
  )
}
