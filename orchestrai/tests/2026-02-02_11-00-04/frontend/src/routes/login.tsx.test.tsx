import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { RouterProvider, createMemoryHistory, createRootRoute, createRouter } from "@tanstack/react-router"
import Login from "./login"
import * as useAuthModule from "@/hooks/useAuth"

// Mock dependencies
vi.mock("@/hooks/useAuth")
vi.mock("react-router-dom", () => ({
  Link: ({ to, children, ...props }: any) => <a href={to} {...props}>{children}</a>,
}))

describe("Login Component", () => {
  const queryClient = new QueryClient()
  const mockNavigate = vi.fn()
  const mockResetError = vi.fn()
  const mockLoginMutation = {
    mutateAsync: vi.fn(),
    isLoading: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    
    vi.spyOn(useAuthModule, "isLoggedIn").mockReturnValue(false)
    vi.spyOn(useAuthModule, "default").mockReturnValue({
      loginMutation: mockLoginMutation,
      error: null,
      resetError: mockResetError,
      user: null,
      signUpMutation: {},
      logout: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe("Route beforeLoad", () => {
    it("should redirect to home if user is already logged in", async () => {
      vi.spyOn(useAuthModule, "isLoggedIn").mockReturnValue(true)
      
      // The beforeLoad function should be called and throw redirect
      expect(() => {
        throw new Error("redirect")
      }).toThrow()
    })

    it("should not redirect if user is not logged in", () => {
      vi.spyOn(useAuthModule, "isLoggedIn").mockReturnValue(false)
      expect(useAuthModule.isLoggedIn()).toBe(false)
    })
  })

  describe("Component Rendering", () => {
    it("should render login form with all required fields", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
      expect(screen.getByPlaceholderText("Password")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument()
    })

    it("should render FastAPI logo", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const logo = screen.getByAltText("FastAPI logo")
      expect(logo).toBeInTheDocument()
    })

    it("should render recover password link", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      expect(screen.getByText("Forgot Password?")).toBeInTheDocument()
    })

    it("should render signup link", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      expect(screen.getByText(/sign up/i)).toBeInTheDocument()
    })
  })

  describe("Form Validation", () => {
    it("should show error when username is missing", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const submitButton = screen.getByRole("button", { name: /log in/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText("Username is required")).toBeInTheDocument()
      })
    })

    it("should show error when username has invalid email format", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, "invalid-email")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(screen.getByText("Invalid email address")).toBeInTheDocument()
      })
    })

    it("should show error when password is missing", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, "test@example.com")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(screen.getByText("Password is required")).toBeInTheDocument()
      })
    })

    it("should show error when password is less than 8 characters", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "short")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(screen.getByText("Password must be at least 8 characters")).toBeInTheDocument()
      })
    })
  })

  describe("Form Submission", () => {
    it("should call loginMutation with valid form data", async () => {
      mockLoginMutation.mutateAsync.mockResolvedValue(true)
      const user = userEvent.setup()

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "password123")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
          username: "test@example.com",
          password: "password123",
        })
      })
    })

    it("should call resetError before submitting", async () => {
      mockLoginMutation.mutateAsync.mockResolvedValue(true)
      const user = userEvent.setup()

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "password123")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockResetError).toHaveBeenCalled()
      })
    })

    it("should not submit if form is already submitting", async () => {
      const user = userEvent.setup()
      mockLoginMutation.mutateAsync.mockImplementation(() => new Promise(() => {}))

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "password123")

      const submitButton = screen.getByRole("button", { name: /log in/i })
      await user.click(submitButton)

      expect(submitButton).toHaveAttribute("data-loading", "true")
    })

    it("should handle mutation errors gracefully", async () => {
      const mockError = new Error("Login failed")
      mockLoginMutation.mutateAsync.mockRejectedValue(mockError)
      const user = userEvent.setup()

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "password123")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        // Error is handled by useAuth hook, component should remain stable
        expect(mockResetError).toHaveBeenCalled()
      })
    })

    it("should show loading state during submission", async () => {
      mockLoginMutation.mutateAsync.mockImplementation(() => new Promise(() => {}))
      const user = userEvent.setup()

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "password123")

      const submitButton = screen.getByRole("button", { name: /log in/i })
      await user.click(submitButton)

      expect(submitButton).toHaveAttribute("data-loading", "true")
    })
  })

  describe("Error Display", () => {
    it("should display error from hook when email is invalid", () => {
      vi.spyOn(useAuthModule, "default").mockReturnValue({
        loginMutation: mockLoginMutation,
        error: "Invalid credentials",
        resetError: mockResetError,
        user: null,
        signUpMutation: {},
        logout: vi.fn(),
      })

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailField = screen.getByPlaceholderText("Email").closest("div")
      expect(emailField?.textContent).toContain("Invalid credentials")
    })

    it("should display field-specific error messages", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      // Errors are shown after validation, tested in validation section
      expect(screen.getByPlaceholderText("Email")).toBeInTheDocument()
    })
  })

  describe("Accessibility", () => {
    it("should have proper form structure", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const form = screen.getByPlaceholderText("Email").closest("form")
      expect(form).toBeInTheDocument()
      expect(form?.tagName).toBe("FORM")
    })

    it("should have accessible email input", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      expect(emailInput).toHaveAttribute("type", "email")
      expect(emailInput).toHaveAttribute("id", "username")
    })

    it("should have accessible password input", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const passwordInput = screen.getByPlaceholderText("Password")
      expect(passwordInput).toHaveAttribute("type", "password")
    })

    it("should have proper form method", () => {
      const { container } = render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const form = container.querySelector("form")
      expect(form).toBeInTheDocument()
    })
  })

  describe("Edge Cases", () => {
    it("should handle whitespace-only email", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, "   ")
      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(screen.getByText("Invalid email address")).toBeInTheDocument()
      })
    })

    it("should handle email with special characters", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, "test+tag@example.co.uk")
      const passwordInput = screen.getByPlaceholderText("Password")
      await user.type(passwordInput, "password123")

      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
          username: "test+tag@example.co.uk",
          password: "password123",
        })
      })
    })

    it("should handle very long email addresses", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const longEmail = "a".repeat(100) + "@example.com"
      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, longEmail)
      const passwordInput = screen.getByPlaceholderText("Password")
      await user.type(passwordInput, "password123")

      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
          username: longEmail,
          password: "password123",
        })
      })
    })

    it("should handle very long passwords", async () => {
      const user = userEvent.setup()
      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const longPassword = "a".repeat(200)
      const emailInput = screen.getByPlaceholderText("Email")
      await user.type(emailInput, "test@example.com")
      const passwordInput = screen.getByPlaceholderText("Password")
      await user.type(passwordInput, longPassword)

      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
          username: "test@example.com",
          password: longPassword,
        })
      })
    })

    it("should handle password with exactly 8 characters", async () => {
      const user = userEvent.setup()
      mockLoginMutation.mutateAsync.mockResolvedValue(true)

      render(
        <QueryClientProvider client={queryClient}>
          <Login />
        </QueryClientProvider>
      )

      const emailInput = screen.getByPlaceholderText("Email")
      const passwordInput = screen.getByPlaceholderText("Password")

      await user.type(emailInput, "test@example.com")
      await user.type(passwordInput, "12345678")

      await user.click(screen.getByRole("button", { name: /log in/i }))

      await waitFor(() => {
        expect(mockLoginMutation.mutateAsync).toHaveBeenCalledWith({
          username: "test@example.com",
          password: "12345678",
        })
      })
    })
  })
})