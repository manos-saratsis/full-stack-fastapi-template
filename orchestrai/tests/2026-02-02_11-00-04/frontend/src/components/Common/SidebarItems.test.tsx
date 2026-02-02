import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import SidebarItems from "./SidebarItems"
import type { UserPublic } from "@/client"

// Mock dependencies
vi.mock("@tanstack/react-query", () => ({
  useQueryClient: vi.fn(),
}))

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children, onClick }: any) => (
    <a href={to} onClick={onClick} data-testid={`link-${to}`}>
      {children}
    </a>
  ),
}))

vi.mock("react-icons/fi", () => ({
  FiHome: () => <div data-testid="icon-home" />,
  FiBriefcase: () => <div data-testid="icon-briefcase" />,
  FiSettings: () => <div data-testid="icon-settings" />,
  FiUsers: () => <div data-testid="icon-users" />,
}))

import { useQueryClient } from "@tanstack/react-query"

describe("SidebarItems", () => {
  const mockQueryClient = {
    getQueryData: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useQueryClient as any).mockReturnValue(mockQueryClient)
  })

  it("should render sidebar items component", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(screen.getByText("Menu")).toBeInTheDocument()
  })

  it("should render menu label", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    const menuLabel = screen.getByText("Menu")
    expect(menuLabel).toBeInTheDocument()
  })

  it("should render dashboard link", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    const dashboardLink = screen.getByTestId("link-/")
    expect(dashboardLink).toBeInTheDocument()
    expect(screen.getByText("Dashboard")).toBeInTheDocument()
  })

  it("should render items link", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    const itemsLink = screen.getByTestId("link-/items")
    expect(itemsLink).toBeInTheDocument()
    expect(screen.getByText("Items")).toBeInTheDocument()
  })

  it("should render user settings link", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    const settingsLink = screen.getByTestId("link-/settings")
    expect(settingsLink).toBeInTheDocument()
    expect(screen.getByText("User Settings")).toBeInTheDocument()
  })

  it("should not render admin link for non-superuser", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "user@example.com",
      is_active: true,
      is_superuser: false,
      full_name: "Regular User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<SidebarItems />)

    expect(screen.queryByTestId("link-/admin")).not.toBeInTheDocument()
    expect(screen.queryByText("Admin")).not.toBeInTheDocument()
  })

  it("should render admin link for superuser", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "admin@example.com",
      is_active: true,
      is_superuser: true,
      full_name: "Admin User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<SidebarItems />)

    const adminLink = screen.getByTestId("link-/admin")
    expect(adminLink).toBeInTheDocument()
    expect(screen.getByText("Admin")).toBeInTheDocument()
  })

  it("should render all default items for superuser", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "admin@example.com",
      is_active: true,
      is_superuser: true,
      full_name: "Admin User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<SidebarItems />)

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
    expect(screen.getByText("Items")).toBeInTheDocument()
    expect(screen.getByText("User Settings")).toBeInTheDocument()
    expect(screen.getByText("Admin")).toBeInTheDocument()
  })

  it("should render home icon for dashboard", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(screen.getByTestId("icon-home")).toBeInTheDocument()
  })

  it("should render briefcase icon for items", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(screen.getByTestId("icon-briefcase")).toBeInTheDocument()
  })

  it("should render settings icon for user settings", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(screen.getByTestId("icon-settings")).toBeInTheDocument()
  })

  it("should render users icon for admin when is superuser", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "admin@example.com",
      is_active: true,
      is_superuser: true,
      full_name: "Admin User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<SidebarItems />)

    expect(screen.getByTestId("icon-users")).toBeInTheDocument()
  })

  it("should call onClose when a link is clicked", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const onClose = vi.fn()
    render(<SidebarItems onClose={onClose} />)

    const dashboardLink = screen.getByTestId("link-/")
    dashboardLink.click()

    expect(onClose).toHaveBeenCalled()
  })

  it("should not call undefined onClose", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(() => {
      const dashboardLink = screen.getByTestId("link-/")
      dashboardLink.click()
    }).not.toThrow()
  })

  it("should render links with correct paths", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(screen.getByTestId("link-/")).toHaveAttribute("href", "/")
    expect(screen.getByTestId("link-/items")).toHaveAttribute("href", "/items")
    expect(screen.getByTestId("link-/settings")).toHaveAttribute("href", "/settings")
  })

  it("should use useQueryClient hook", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(useQueryClient).toHaveBeenCalled()
  })

  it("should get current user from query client", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    expect(mockQueryClient.getQueryData).toHaveBeenCalledWith(["currentUser"])
  })

  it("should handle null user data gracefully", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const { container } = render(<SidebarItems />)

    expect(container).toBeTruthy()
  })

  it("should handle undefined user data gracefully", () => {
    mockQueryClient.getQueryData.mockReturnValue(undefined)

    const { container } = render(<SidebarItems />)

    expect(container).toBeTruthy()
  })

  it("should create correct number of list items for non-superuser", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    render(<SidebarItems />)

    const links = screen.getAllByRole("link")
    expect(links).toHaveLength(3) // Dashboard, Items, Settings
  })

  it("should create correct number of list items for superuser", () => {
    const currentUser: UserPublic = {
      id: 1,
      email: "admin@example.com",
      is_active: true,
      is_superuser: true,
      full_name: "Admin User",
    }
    mockQueryClient.getQueryData.mockReturnValue(currentUser)

    render(<SidebarItems />)

    const links = screen.getAllByRole("link")
    expect(links).toHaveLength(4) // Dashboard, Items, Settings, Admin
  })

  it("should render with optional onClose prop", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const { container } = render(<SidebarItems onClose={() => {}} />)

    expect(container).toBeTruthy()
  })

  it("should call onClose multiple times if multiple links are clicked", () => {
    mockQueryClient.getQueryData.mockReturnValue(null)

    const onClose = vi.fn()
    render(<SidebarItems onClose={onClose} />)

    const dashboardLink = screen.getByTestId("link-/")
    const itemsLink = screen.getByTestId("link-/items")

    dashboardLink.click()
    itemsLink.click()

    expect(onClose).toHaveBeenCalledTimes(2)
  })
})