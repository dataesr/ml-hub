import React, { ReactNode } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Link } from "react-router-dom";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import Router from "./router";
import "./styles/index.scss";
import { DSFRConfig } from "@dataesr/dsfr-plus";

const queryClient = new QueryClient();

type RouterLinkProps = {
  href: string;
  replace?: boolean;
  target?: string;
  children?: ReactNode;
};

const RouterLink = ({ href, replace, target, ...props }: RouterLinkProps) => {
  if (target === "_blank") return <a href={href} target={target} {...props} />;
  return <Link to={href} replace={replace} {...props} />;
};

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <DSFRConfig routerComponent={RouterLink}>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <ReactQueryDevtools />
          <Router />
        </QueryClientProvider>
      </BrowserRouter>
    </DSFRConfig>
  </React.StrictMode>
);
