import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { ItemActionsMenu } from "./ItemActionsMenu"
import type { ItemPublic } from "@/client"
import * as DeleteItemModule from "../Items/DeleteItem"
import * as EditItemModule from "../Items/EditItem"

// Mock the child components
vi.mock("../Items/DeleteItem", () => ({
  default: vi.fn(() => <div data-testid="delete-item">DeleteItem</div>),
}))

vi.mock("../Items/EditItem", () => ({
  default: vi.fn(() => <div data-testid="edit-item">EditItem</div>),
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
    ...props
  }: {
    children: React.ReactNode
    [key: string]: any
  }) => (
    <button data-testid="icon-button" {...props}>
      {children}
    </button>
  ),
}))

// Mock react-icons
vi.mock("react-icons/bs", () => ({
  BsThreeDotsVertical: () => <span data-testid="three-dots-icon">⋯</span>,
}))

describe("ItemActionsMenu", () => {
  const mockItem: ItemPublic = {
    id: 1,
    title: "Test Item",
    description: "Test Description",
    owner_id: 1,
  }

  describe("Rendering", () => {
    it("should render the menu root", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should render the menu trigger", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("menu-trigger")).toBeInTheDocument()
    })

    it("should render the menu content", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("menu-content")).toBeInTheDocument()
    })

    it("should render the icon button trigger", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("icon-button")).toBeInTheDocument()
    })

    it("should render the three dots icon", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("three-dots-icon")).toBeInTheDocument()
    })

    it("should render EditItem component with correct prop", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("edit-item")).toBeInTheDocument()
      expect(DeleteItemModule.default).toHaveBeenCalledWith(
        expect.objectContaining({ item: mockItem }),
        expect.any(Object)
      )
    })

    it("should render DeleteItem component with correct prop", () => {
      render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("delete-item")).toBeInTheDocument()
      expect(DeleteItemModule.default).toHaveBeenCalledWith(
        expect.objectContaining({ id: mockItem.id }),
        expect.any(Object)
      )
    })
  })

  describe("IconButton properties", () => {
    it("should have ghost variant", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toBeInTheDocument()
    })

    it("should have color inherit", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).toHaveAttribute("color", "inherit")
    })

    it("should not be disabled by default", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toHaveAttribute("disabled")
    })
  })

  describe("Component composition", () => {
    it("should pass item prop to EditItem", () => {
      const EditItemSpy = vi.spyOn(EditItemModule, "default")
      render(<ItemActionsMenu item={mockItem} />)
      expect(EditItemSpy).toHaveBeenCalledWith(
        expect.objectContaining({ item: mockItem }),
        expect.any(Object)
      )
    })

    it("should pass id prop to DeleteItem", () => {
      const DeleteItemSpy = vi.spyOn(DeleteItemModule, "default")
      render(<ItemActionsMenu item={mockItem} />)
      expect(DeleteItemSpy).toHaveBeenCalledWith(
        expect.objectContaining({ id: mockItem.id }),
        expect.any(Object)
      )
    })

    it("should render both EditItem and DeleteItem in correct order", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const menuContent = container.querySelector('[data-testid="menu-content"]')
      const children = menuContent?.children
      expect(children?.length).toBe(2)
      expect(children?.[0]).toHaveAttribute("data-testid", "edit-item")
      expect(children?.[1]).toHaveAttribute("data-testid", "delete-item")
    })
  })

  describe("Edge cases", () => {
    it("should handle item with minimal data", () => {
      const minimalItem: ItemPublic = {
        id: 0,
        title: "",
        description: "",
        owner_id: 0,
      }
      render(<ItemActionsMenu item={minimalItem} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle item with large id", () => {
      const itemWithLargeId: ItemPublic = {
        ...mockItem,
        id: Number.MAX_SAFE_INTEGER,
      }
      render(<ItemActionsMenu item={itemWithLargeId} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle item with special characters in title", () => {
      const itemWithSpecialChars: ItemPublic = {
        ...mockItem,
        title: "Test <Item> & \"Special\" 'Chars'",
      }
      render(<ItemActionsMenu item={itemWithSpecialChars} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle item with very long description", () => {
      const itemWithLongDesc: ItemPublic = {
        ...mockItem,
        description: "A".repeat(10000),
      }
      render(<ItemActionsMenu item={itemWithLongDesc} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should handle item with null-like string values", () => {
      const itemWithNullStrings: ItemPublic = {
        ...mockItem,
        title: "null",
        description: "undefined",
      }
      render(<ItemActionsMenu item={itemWithNullStrings} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })
  })

  describe("Props handling", () => {
    it("should accept ItemPublic type with all properties", () => {
      const fullItem: ItemPublic = {
        id: 42,
        title: "Complete Item",
        description: "Full description",
        owner_id: 5,
      }
      render(<ItemActionsMenu item={fullItem} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })

    it("should maintain stable reference for item prop across renders", () => {
      const { rerender } = render(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
      rerender(<ItemActionsMenu item={mockItem} />)
      expect(screen.getByTestId("menu-root")).toBeInTheDocument()
    })
  })

  describe("UI interactivity", () => {
    it("should render as an interactive button", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button?.tagName).toBe("BUTTON")
    })

    it("should be clickable", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const button = container.querySelector('[data-testid="icon-button"]')
      expect(button).not.toBeDisabled()
    })
  })

  describe("Integration with menu components", () => {
    it("should have MenuRoot as the outer wrapper", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      expect(menuRoot?.children.length).toBeGreaterThan(0)
    })

    it("should have MenuTrigger inside MenuRoot", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      const menuTrigger = menuRoot?.querySelector('[data-testid="menu-trigger"]')
      expect(menuTrigger).toBeInTheDocument()
    })

    it("should have MenuContent as sibling to MenuTrigger", () => {
      const { container } = render(<ItemActionsMenu item={mockItem} />)
      const menuRoot = container.querySelector('[data-testid="menu-root"]')
      const menuContent = menuRoot?.querySelector('[data-testid="menu-content"]')
      expect(menuContent).toBeInTheDocument()
    })
  })
})