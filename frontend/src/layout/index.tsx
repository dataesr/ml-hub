import { Outlet } from "react-router-dom";
import Header from "./header";
import MainFooter from "./footer";

export default function Layout() {
  return (
    <>
      <Header />
      <Outlet />
      <MainFooter />
    </>
  );
}
