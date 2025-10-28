import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Model from "./pages/models/model"
import Jobs from "./pages/jobs"
import Models from "./pages/models"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/models" element={<Models />} />
        <Route path="/models/:owner/:name" element={<Model />} />
        <Route path="/jobs" element={<Jobs />} />
      </Route>
    </Routes>
  )
}
