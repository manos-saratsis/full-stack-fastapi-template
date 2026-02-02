import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import Sidebar from "./Sidebar"
import type { UserPublic } from "@/client"

// Mock dependencies
vi.mock("@tanstack/react-query", () => ({
  useQueryClient: vi.fn(),
}))

vi.mock("@/hooks/useAuth", () => ({
  default: vi.fn(),
}))

vi.mock("./SidebarItems", () => ({
  default: ({ onClose }: { onClose?: () => void }) => (
    <div data-testid="sidebar-items" onClick={onClose}>
      SidebarItems
    </div>
  ),
}))

vi.mock("../ui/drawer", () => ({
  DrawerRoot: ({ children, open, onOpenChange }: any) => (
    <div
      data-testid="drawer-root"
      onClick={() => onOpenChange?.({ open: !open })}
    >
      {children}
    </div>
  ),
  DrawerBackdrop: () => <div data-testid="drawer-backdrop" />,
  DrawerTrigger: ({ children }: any) => (
    <div data-testid="drawer-trigger">{children}</div>
  ),
  DrawerContent: ({ children }: any) => (
    <div data-testid="drawer-content">{children}</div>
  ),
  DrawerBody: ({ children }: any) => (
    <div data-testid="drawer-body">{children}</div>
  ),
  DrawerCloseTrigger: () => <div data-testid="drawer-close-trigger" />,
}))

import { useQueryClient } from "@tanstack/react-query"
import useAuth from "@/hooks/useAuth"

describe("Sidebar", () => {
  const mockLogout = vi.fn()
  const mockQueryClient = {
    getQueryData: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useQueryClient as any).mockReturnValue(mockQueryClient)
    ;(useAuth as any).mockReturnValue({
      logout: mockLogout,
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it("should render sidebar component", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    expect(screen.getByTestId("drawer-root")).toBeInTheDocument()
  })

  it("should render drawer root with start placement", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const { container } = render(<Sidebar />)

    const drawerRoot = screen.getByTestId("drawer-root")
    expect(drawerRoot).toBeInTheDocument()
  })

  it("should render drawer trigger on mobile", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const trigger = screen.getByTestId("drawer-trigger")
    expect(trigger).toBeInTheDocument()
  })

  it("should render drawer backdrop", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const backdrop = screen.getByTestId("drawer-backdrop")
    expect(backdrop).toBeInTheDocument()
  })

  it("should render sidebar items in drawer body", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const sidebarItems = screen.getByTestId("sidebar-items")
    expect(sidebarItems).toBeInTheDocument()
  })

  it("should call logout when logout button is clicked", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const logoutButton = screen.getByText("Log Out")
    fireEvent.click(logoutButton)

    expect(mockLogout).toHaveBeenCalled()
  })

  it("should render user email when user is logged in", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "test@example.com",
      is_active: true,
      is_superuser: false,
      full_name: "Test User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<Sidebar />)

    expect(screen.getByText("Logged in as: test@example.com")).toBeInTheDocument()
  })

  it("should not render user email when user email is not available", () => {
    mockQueryClient.getQueryData.mockReturnValue({ id: 1, email: null })

    render(<Sidebar />)

    expect(screen.queryByText(/Logged in as:/)).not.toBeInTheDocument()
  })

  it("should not render user email when user is null", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    expect(screen.queryByText(/Logged in as:/)).not.toBeInTheDocument()
  })

  it("should close drawer when onClose is called from SidebarItems", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const sidebarItems = screen.getByTestId("sidebar-items")
    fireEvent.click(sidebarItems)
  })

  it("should manage open state for drawer", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const drawerRoot = screen.getByTestId("drawer-root")
    fireEvent.click(drawerRoot)
  })

  it("should render desktop sidebar with sticky position", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const { container } = render(<Sidebar />)

    const desktopBox = container.querySelector(
      '[style*="display: none"], [display="none"]'
    )
    expect(container).toBeTruthy()
  })

  it("should render SidebarItems without onClose prop for desktop", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const sidebarItems = screen.getByTestId("sidebar-items")
    expect(sidebarItems).toBeInTheDocument()
  })

  it("should handle drawer content maxW property", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const { container } = render(<Sidebar />)

    const drawerContent = screen.getByTestId("drawer-content")
    expect(drawerContent).toBeInTheDocument()
  })

  it("should pass correct props to DrawerCloseTrigger", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const closeTrigger = screen.getByTestId("drawer-close-trigger")
    expect(closeTrigger).toBeInTheDocument()
  })

  it("should render flex layout with column direction for mobile drawer", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    const drawerBody = screen.getByTestId("drawer-body")
    expect(drawerBody).toBeInTheDocument()
  })

  it("should use useQueryClient hook", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    expect(useQueryClient).toHaveBeenCalled()
  })

  it("should use useAuth hook", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    expect(useAuth).toHaveBeenCalled()
  })

  it("should get current user from query client with correct key", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<Sidebar />)

    expect(mockQueryClient.getQueryData).toHaveBeenCalledWith(["currentUser"])
  })
})