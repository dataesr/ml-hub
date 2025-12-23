import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Explore from "./pages/explore"
import Run from "./pages/run"
import Jobs from "./pages/jobs";

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/run" element={<Run />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/jobs" element={<Jobs />} />
      </Route>
    </Routes>
  )
}
