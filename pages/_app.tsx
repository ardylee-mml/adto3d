import type { AppProps } from "next/app";
import { createRoot } from "react-dom/client";
import React, { useEffect } from "react";

if (process.env.NODE_ENV === "development") {
  if (module.hot) {
    module.hot.accept();
  }
}

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Clean up any resources when component unmounts
    return () => {
      // Cleanup code here if needed
    };
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
