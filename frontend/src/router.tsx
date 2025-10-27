import { Route, Routes } from "react-router-dom";

import Layout from "./layout";
import Home from "./pages/home"
import Model from "./pages/model"
import Train from "./pages/train"

export default function Router() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/train" element={<Train />} />
        <Route path="/model/:owner/:name" element={<Model />} />
      </Route>
    </Routes>
  )
}
