import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Model from "./pages/models/model"
import Jobs from "./pages/jobs"
import Models from "./pages/models"
import JobsSubmit from "./pages/jobs/submit"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/models" element={<Models />} />
        <Route path="/models/:owner/:name" element={<Model />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/submit" element={<JobsSubmit />} />
      </Route>
    </Routes>
  )
}
