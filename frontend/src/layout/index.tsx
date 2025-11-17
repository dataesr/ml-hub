import { Outlet } from "react-router-dom";
import { Container } from "@dataesr/dsfr-plus"
import Header from "./header"
import MainFooter from "./footer"

export default function Layout() {
  return (
    <>
      <Header />
      <Container as="main" role="main" fluid>
        <Outlet />
      </Container>
      <MainFooter />
    </>
  )
}
