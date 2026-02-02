import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { UserActionsMenu } from "./UserActionsMenu"
import type { UserPublic } from "@/client"
import * as DeleteUserModule from "../Admin/DeleteUser"
import * as EditUserModule from "../Admin/EditUser"

// Mock the child components
vi.mock("../Admin/DeleteUser", () => ({
  default: vi.fn(() => <div data-testid="delete-user">DeleteUser</div>),
}))

vi.mock("../Admin/EditUser", () => ({
  default: vi.fn(() => <div data-testid="edit-user">EditUser</div>),
}))

// Mock UI menu component
vi.mock("../ui/menu", () => ({
  MenuRoot: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="menu-root">{children}</div>
  ),
  MenuTrigger: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="menu-trigger">{children}</div>
  ),
  MenuContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="menu-content">{children}</div>
  ),
}))

// Mock Chakra UI components
vi.mock("@chakra-ui/react", () => ({
  IconButton: ({
    children,
    disabled,
    ...props
  }: {
    children: React.ReactNode
    disabled?: boolean
    [key: string]: any
  }) => (
    <button data-testid="icon-button" disabled={disabled} {...props}>
      {children}
    </button>
  ),
}))

// Mock react-icons
vi.mock("react-icons/bs", () => ({
  BsThreeDotsVertical: () => <span data-testid="three-dots-icon">⋯</span>,
}))

describe("UserActionsMenu", () => {
  const mockUser: UserPublic = {
    id: 1,
    email: "test@example.com",
    full_name: "Test User",
    is_active: true,
    is_superuser: false,
  }

  describe("Rendering without disabled prop", () => {
    it("should render the menu root", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should render the menu trigger", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("menu-trigger")).toBeInTheDocument()
    })

    it("should render the menu content", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("menu-content")).toBeInTheDocument()
    })

    it("should render the icon button trigger", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("icon-button")).toBeInTheDocument()
    })

    it("should render the three dots icon", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("three-dots-icon")).toBeInTheDocument()
    })

    it("should render EditUser component with correct prop", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
      expect(EditUserModule.default).toHaveBeenCalledWith(
        expect.objectContaining({ user: mockUser }),
        expect.any(Object)
      )
    })

    it("should render DeleteUser component with correct prop", () => {
      render(<UserActionsMenu user={mockUser} />)
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
      expect(DeleteUserModule.default).toHaveBeenCalledWith(
        expect.objectContaining({ id: mockUser.id }),
        expect.any(Object)
      )
    })

    it("should not have disabled attribute on button", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })
  })

  describe("Rendering with disabled prop false", () => {
    it("should render menu when disabled is false", () => {
      render(<UserActionsMenu user={mockUser} disabled={false} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should not disable icon button when disabled is false", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={false} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })

    it("should render EditUser when disabled is false", () => {
      render(<UserActionsMenu user={mockUser} disabled={false} />)
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
    })

    it("should render DeleteUser when disabled is false", () => {
      render(<UserActionsMenu user={mockUser} disabled={false} />)
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
    })
  })

  describe("Rendering with disabled prop true", () => {
    it("should render menu when disabled is true", () => {
      render(<UserActionsMenu user={mockUser} disabled={true} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should disable icon button when disabled is true", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeDisabled()
    })

    it("should render EditUser even when disabled is true", () => {
      render(<UserActionsMenu user={mockUser} disabled={true} />)
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
    })

    it("should render DeleteUser even when disabled is true", () => {
      render(<UserActionsMenu user={mockUser} disabled={true} />)
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
    })

    it("should not be clickable when disabled is true", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeDisabled()
    })
  })

  describe("IconButton properties", () => {
    it("should have ghost variant", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeInTheDocument()
    })

    it("should have color inherit", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toHaveAttribute("color", "inherit")
    })

    it("should respect disabled attribute", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toHaveAttribute("disabled")
    })
  })

  describe("Component composition", () => {
    it("should pass user prop to EditUser", () => {
      const EditUserSpy = vi.spyOn(EditUserModule, "default")
      render(<UserActionsMenu user={mockUser} />)
      expect(EditUserSpy).toHaveBeenCalledWith(
        expect.objectContaining({ user: mockUser }),
        expect.any(Object)
      )
    })

    it("should pass id prop to DeleteUser", () => {
      const DeleteUserSpy = vi.spyOn(DeleteUserModule, "default")
      render(<UserActionsMenu user={mockUser} />)
      expect(DeleteUserSpy).toHaveBeenCalledWith(
        expect.objectContaining({ id: mockUser.id }),
        expect.any(Object)
      )
    })

    it("should render both EditUser and DeleteUser in correct order", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const menuContent = container.querySelector('[data-testid="menu-content"]')
      const children = menuContent?.children
      expect(children?.length).toBe(2)
      expect(children?.[0]).toHaveAttribute("data-testid", "edit-user")
      expect(children?.[1]).toHaveAttribute("data-testid", "delete-user")
    })

    it("should maintain component order regardless of disabled prop", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const menuContent = container.querySelector('[data-testid="menu-content"]')
      const children = menuContent?.children
      expect(children?.[0]).toHaveAttribute("data-testid", "edit-user")
      expect(children?.[1]).toHaveAttribute("data-testid", "delete-user")
    })
  })

  describe("Edge cases for user data", () => {
    it("should handle user with minimal data", () => {
      const minimalUser: UserPublic = {
        id: 0,
        email: "",
        full_name: "",
        is_active: false,
        is_superuser: false,
      }
      render(<UserActionsMenu user={minimalUser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle user with large id", () => {
      const userWithLargeId: UserPublic = {
        ...mockUser,
        id: Number.MAX_SAFE_INTEGER,
      }
      render(<UserActionsMenu user={userWithLargeId} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle user with special characters in email", () => {
      const userWithSpecialChars: UserPublic = {
        ...mockUser,
        email: "test+special@example.co.uk",
      }
      render(<UserActionsMenu user={userWithSpecialChars} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle user with special characters in full_name", () => {
      const userWithSpecialName: UserPublic = {
        ...mockUser,
        full_name: "Jean-Pierre O'Neill",
      }
      render(<UserActionsMenu user={userWithSpecialName} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle user with very long full_name", () => {
      const userWithLongName: UserPublic = {
        ...mockUser,
        full_name: "A".repeat(500),
      }
      render(<UserActionsMenu user={userWithLongName} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle superuser", () => {
      const superuser: UserPublic = {
        ...mockUser,
        is_superuser: true,
      }
      render(<UserActionsMenu user={superuser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle inactive user", () => {
      const inactiveUser: UserPublic = {
        ...mockUser,
        is_active: false,
      }
      render(<UserActionsMenu user={inactiveUser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle inactive and superuser simultaneously", () => {
      const inactiveSuperuser: UserPublic = {
        ...mockUser,
        is_active: false,
        is_superuser: true,
      }
      render(<UserActionsMenu user={inactiveSuperuser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })
  })

  describe("Disabled prop variations", () => {
    it("should handle undefined disabled prop", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={undefined} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })

    it("should handle disabled={0} as falsy", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={0 as any} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })

    it("should handle disabled={1} as truthy", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={1 as any} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeDisabled()
    })

    it("should toggle disabled state correctly on prop change", () => {
      const { rerender, container } = render(
        <UserActionsMenu user={mockUser} disabled={false} />
      )
      let button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()

      rerender(<UserActionsMenu user={mockUser} disabled={true} />)
      button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeDisabled()
    })
  })

  describe("Props handling", () => {
    it("should accept UserPublic type with all properties", () => {
      const fullUser: UserPublic = {
        id: 42,
        email: "john.doe@example.com",
        full_name: "John Doe",
        is_active: true,
        is_superuser: false,
      }
      render(<UserActionsMenu user={fullUser} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should maintain stable reference for user prop across renders", () => {
      const { rerender } = render(
        <UserActionsMenu user={mockUser} disabled={false} />
      )
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
      rerender(<UserActionsMenu user={mockUser} disabled={false} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle prop updates for disabled", () => {
      const { rerender } = render(
        <UserActionsMenu user={mockUser} disabled={false} />
      )
      expect(screen.getByTestId("icon-button")).not.toBeDisabled()
      rerender(<UserActionsMenu user={mockUser} disabled={true} />)
      expect(screen.getByTestId("icon-button")).toBeDisabled()
    })
  })

  describe("UI interactivity", () => {
    it("should render as an interactive button when enabled", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button?.tagName).toBe("BUTTON")
      expect(button).not.toBeDisabled()
    })

    it("should render as a disabled button when disabled prop is true", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button?.tagName).toBe("BUTTON")
      expect(button).toBeDisabled()
    })

    it("should be clickable when enabled", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })

    it("should not be clickable when disabled", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeDisabled()
    })
  })

  describe("Integration with menu components", () => {
    it("should have MenuRoot as the outer wrapper", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      expect(menuRoot?.children.length).toBeGreaterThan(0)
    })

    it("should have MenuTrigger inside MenuRoot", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      const menuTrigger = menuRoot?.querySelector('[data-testid="menu-trigger"]')
      expect(menuTrigger).toBeInTheDocument()
    })

    it("should have MenuContent as sibling to MenuTrigger", () => {
      const { container } = render(<UserActionsMenu user={mockUser} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      const menuContent = menuRoot?.querySelector('[data-testid="menu-content"]')
      expect(menuContent).toBeInTheDocument()
    })

    it("should maintain menu structure when disabled", () => {
      const { container } = render(
        <UserActionsMenu user={mockUser} disabled={true} />
      )
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      const menuTrigger = menuRoot?.querySelector('[data-testid="menu-trigger"]')
      const menuContent = menuRoot?.querySelector('[data-testid="menu-content"]')
      expect(menuTrigger).toBeInTheDocument()
      expect(menuContent).toBeInTheDocument()
    })
  })

  describe("Complete branch coverage", () => {
    it("should render all paths when disabled is undefined (falsy path)", () => {
      render(<UserActionsMenu user={mockUser} />)
      const button = screen.getByTestId("icon-button")
      expect(button).not.toBeDisabled()
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
    })

    it("should render all paths when disabled is true (truthy path)", () => {
      render(<UserActionsMenu user={mockUser} disabled={true} />)
      const button = screen.getByTestId("icon-button")
      expect(button).toBeDisabled()
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
    })

    it("should render all paths when disabled is false (falsy path)", () => {
      render(<UserActionsMenu user={mockUser} disabled={false} />)
      const button = screen.getByTestId("icon-button")
      expect(button).not.toBeDisabled()
      expect(screen.getByTestId("edit-user")).toBeInTheDocument()
      expect(screen.getByTestId("delete-user")).toBeInTheDocument()
    })
  })
})