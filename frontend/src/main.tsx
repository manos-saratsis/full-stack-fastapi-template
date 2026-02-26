import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { RouterProvider, createRouter } from "@tanstack/react-router"
import React, { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { routeTree } from "./routeTree.gen"

import { ApiError, OpenAPI } from "./client"
import { CustomProvider } from "./components/ui/provider"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
  }
}

// Initialize Dynatrace user identification and session properties
const initializeDynatrace = () => {
  if (typeof (window as any).dtrum !== 'undefined') {
    // Identify user if authenticated
    const accessToken = localStorage.getItem("access_token")
    if (accessToken) {
      try {
        const payload = JSON.parse(atob(accessToken.split('.')[1]))
        if (payload.sub) {
          (window as any).dtrum.identifyUser(payload.sub)
        }
      } catch (e) {
        // Token parsing failed, continue without user identification
      }
    }

    // Add session properties
    (window as any).dtrum.sendSessionProperties({
      'app.name': 'frontend',
      'app.environment': import.meta.env.MODE || 'development',
      'app.version': import.meta.env.VITE_APP_VERSION || '1.0.0'
    })
  }
}

// Initialize Dynatrace when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeDynatrace)
} else {
  initializeDynatrace()
}

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CustomProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </CustomProvider>
  </StrictMode>,
)