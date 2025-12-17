import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Explore from "./pages/explore"
import Run from "./pages/run"
import Analyze from "./pages/analyze"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/run" element={<Run />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/configure" element={<Home />} />
      </Route>
    </Routes>
  )
}
