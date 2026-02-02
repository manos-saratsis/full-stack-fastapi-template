import { render, screen } from "@testing-library/react"
import * as React from "react"
import { vi, describe, it, expect } from "vitest"
import {
  DrawerContent,
  DrawerCloseTrigger,
  DrawerTrigger,
  DrawerRoot,
  DrawerFooter,
  DrawerHeader,
  DrawerBody,
  DrawerBackdrop,
  DrawerDescription,
  DrawerTitle,
  DrawerActionTrigger,
} from "./drawer"
import * as ChakraDrawer from "@chakra-ui/react"

// Mock Chakra Drawer components
vi.mock("@chakra-ui/react", async () => {
  const actual = await vi.importActual("@chakra-ui/react")
  return {
    ...actual,
    Drawer: {
      Root: ({ children }: any) => <div data-testid="drawer-root">{children}</div>,
      Content: React.forwardRef(({ children, ...props }: any, ref: any) => (
        <div data-testid="drawer-content" ref={ref} {...props}>
          {children}
        </div>
      )),
      Positioner: ({ children, padding }: any) => (
        <div data-testid="drawer-positioner" data-padding={padding}>
          {children}
        </div>
      ),
      CloseTrigger: ({ children, ...props }: any) => (
        <button data-testid="drawer-close-trigger" {...props}>
          {children}
        </button>
      ),
      Backdrop: () => <div data-testid="drawer-backdrop" />,
      Footer: ({ children }: any) => <div data-testid="drawer-footer">{children}</div>,
      Header: ({ children }: any) => <div data-testid="drawer-header">{children}</div>,
      Body: ({ children }: any) => <div data-testid="drawer-body">{children}</div>,
      Description: ({ children }: any) => <p data-testid="drawer-description">{children}</p>,
      Title: ({ children }: any) => <h2 data-testid="drawer-title">{children}</h2>,
      Trigger: ({ children }: any) => <button data-testid="drawer-trigger">{children}</button>,
      ActionTrigger: ({ children }: any) => (
        <button data-testid="drawer-action-trigger">{children}</button>
      ),
    },
    Portal: ({ children, disabled, container }: any) =>
      disabled ? (
        children
      ) : (
        <div data-testid="portal" data-disabled={disabled}>
          {children}
        </div>
      ),
  }
})

vi.mock("./close-button", () => ({
  CloseButton: React.forwardRef(({ children, ...props }: any, ref: any) => (
    <button data-testid="close-button" ref={ref} {...props}>
      {children}
    </button>
  )),
}))

describe("DrawerContent", () => {
  it("should render with portalled enabled by default", () => {
    render(
      <DrawerContent>
        <div>Test Content</div>
      </DrawerContent>,
    )
    const portal = screen.getByTestId("portal")
    expect(portal).toBeInTheDocument()
    expect(portal).toHaveAttribute("data-disabled", "false")
  })

  it("should render with portalled disabled when portalled prop is false", () => {
    render(
      <DrawerContent portalled={false}>
        <div>Test Content</div>
      </DrawerContent>,
    )
    const content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()
  })

  it("should render positioner and content elements", () => {
    render(
      <DrawerContent>
        <div>Test Content</div>
      </DrawerContent>,
    )
    const positioner = screen.getByTestId("drawer-positioner")
    const content = screen.getByTestId("drawer-content")
    expect(positioner).toBeInTheDocument()
    expect(content).toBeInTheDocument()
  })

  it("should render children content", () => {
    render(
      <DrawerContent>
        <p>Child Content Text</p>
      </DrawerContent>,
    )
    expect(screen.getByText("Child Content Text")).toBeInTheDocument()
  })

  it("should forward ref to DrawerContent", () => {
    const ref = React.createRef<HTMLDivElement>()
    render(
      <DrawerContent ref={ref}>
        <div>Test Content</div>
      </DrawerContent>,
    )
    expect(ref.current).toBeTruthy()
  })

  it("should pass through custom props to ChakraDrawer.Content", () => {
    render(
      <DrawerContent data-custom="test-value" className="custom-class">
        <div>Test Content</div>
      </DrawerContent>,
    )
    const content = screen.getByTestId("drawer-content")
    expect(content).toHaveAttribute("data-custom", "test-value")
  })

  it("should use custom portalRef when provided", () => {
    const portalRef = React.createRef<HTMLElement>()
    render(
      <DrawerContent portalRef={portalRef}>
        <div>Test Content</div>
      </DrawerContent>,
    )
    const portal = screen.getByTestId("portal")
    expect(portal).toBeInTheDocument()
  })

  it("should pass offset prop to Positioner as padding", () => {
    render(
      <DrawerContent offset="4">
        <div>Test Content</div>
      </DrawerContent>,
    )
    const positioner = screen.getByTestId("drawer-positioner")
    expect(positioner).toHaveAttribute("data-padding", "4")
  })

  it("should handle undefined offset", () => {
    render(
      <DrawerContent offset={undefined}>
        <div>Test Content</div>
      </DrawerContent>,
    )
    const positioner = screen.getByTestId("drawer-positioner")
    expect(positioner).toBeInTheDocument()
  })

  it("should set asChild to false on ChakraDrawer.Content", () => {
    render(
      <DrawerContent>
        <div>Test</div>
      </DrawerContent>,
    )
    const content = screen.getByTestId("drawer-content")
    expect(content).toHaveAttribute("asChild", "false")
  })

  it("should combine portalled and offset props correctly", () => {
    render(
      <DrawerContent portalled={true} offset="8">
        <div>Test</div>
      </DrawerContent>,
    )
    const portal = screen.getByTestId("portal")
    const positioner = screen.getByTestId("drawer-positioner")
    expect(portal).toBeInTheDocument()
    expect(positioner).toHaveAttribute("data-padding", "8")
  })

  it("should handle multiple children nodes", () => {
    render(
      <DrawerContent>
        <div>First</div>
        <div>Second</div>
      </DrawerContent>,
    )
    expect(screen.getByText("First")).toBeInTheDocument()
    expect(screen.getByText("Second")).toBeInTheDocument()
  })
})

describe("DrawerCloseTrigger", () => {
  it("should render close button", () => {
    render(<DrawerCloseTrigger />)
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton).toBeInTheDocument()
  })

  it("should pass size sm to close button", () => {
    render(<DrawerCloseTrigger />)
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton).toHaveAttribute("size", "sm")
  })

  it("should forward ref correctly", () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<DrawerCloseTrigger ref={ref} />)
    expect(ref.current).toBeTruthy()
  })

  it("should have position absolute with top and insetEnd styles", () => {
    render(<DrawerCloseTrigger />)
    const closeTrigger = screen.getByTestId("drawer-close-trigger")
    expect(closeTrigger).toHaveAttribute("position", "absolute")
    expect(closeTrigger).toHaveAttribute("top", "2")
    expect(closeTrigger).toHaveAttribute("insetEnd", "2")
  })

  it("should pass through additional props", () => {
    render(
      <DrawerCloseTrigger data-testid="custom-close" aria-label="Close drawer" />,
    )
    const closeTrigger = screen.getByTestId("custom-close")
    expect(closeTrigger).toHaveAttribute("aria-label", "Close drawer")
  })

  it("should set asChild to true on ChakraDrawer.CloseTrigger", () => {
    render(<DrawerCloseTrigger />)
    const closeTrigger = screen.getByTestId("drawer-close-trigger")
    expect(closeTrigger).toHaveAttribute("asChild", "true")
  })

  it("should not render children prop if not provided", () => {
    const { container } = render(<DrawerCloseTrigger />)
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton.textContent).toBe("")
  })
})

describe("Drawer exported components", () => {
  it("should export DrawerTrigger from ChakraDrawer.Trigger", () => {
    expect(DrawerTrigger).toBeDefined()
    expect(DrawerTrigger).toBe(ChakraDrawer.Trigger)
  })

  it("should export DrawerRoot from ChakraDrawer.Root", () => {
    expect(DrawerRoot).toBeDefined()
    expect(DrawerRoot).toBe(ChakraDrawer.Root)
  })

  it("should export DrawerFooter from ChakraDrawer.Footer", () => {
    expect(DrawerFooter).toBeDefined()
    expect(DrawerFooter).toBe(ChakraDrawer.Footer)
  })

  it("should export DrawerHeader from ChakraDrawer.Header", () => {
    expect(DrawerHeader).toBeDefined()
    expect(DrawerHeader).toBe(ChakraDrawer.Header)
  })

  it("should export DrawerBody from ChakraDrawer.Body", () => {
    expect(DrawerBody).toBeDefined()
    expect(DrawerBody).toBe(ChakraDrawer.Body)
  })

  it("should export DrawerBackdrop from ChakraDrawer.Backdrop", () => {
    expect(DrawerBackdrop).toBeDefined()
    expect(DrawerBackdrop).toBe(ChakraDrawer.Backdrop)
  })

  it("should export DrawerDescription from ChakraDrawer.Description", () => {
    expect(DrawerDescription).toBeDefined()
    expect(DrawerDescription).toBe(ChakraDrawer.Description)
  })

  it("should export DrawerTitle from ChakraDrawer.Title", () => {
    expect(DrawerTitle).toBeDefined()
    expect(DrawerTitle).toBe(ChakraDrawer.Title)
  })

  it("should export DrawerActionTrigger from ChakraDrawer.ActionTrigger", () => {
    expect(DrawerActionTrigger).toBeDefined()
    expect(DrawerActionTrigger).toBe(ChakraDrawer.ActionTrigger)
  })
})

describe("DrawerContent - Edge Cases", () => {
  it("should handle null children", () => {
    render(<DrawerContent>{null}</DrawerContent>)
    const content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()
  })

  it("should handle undefined children", () => {
    render(<DrawerContent>{undefined}</DrawerContent>)
    const content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()
  })

  it("should handle empty string children", () => {
    render(<DrawerContent>{""}</DrawerContent>)
    const content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()
  })

  it("should render with all props set", () => {
    render(
      <DrawerContent portalled={true} offset="6">
        <div>Content</div>
      </DrawerContent>,
    )
    const positioner = screen.getByTestId("drawer-positioner")
    expect(positioner).toHaveAttribute("data-padding", "6")
  })

  it("should render with portalled disabled and custom offset", () => {
    render(
      <DrawerContent portalled={false} offset="10">
        <div>Content</div>
      </DrawerContent>,
    )
    const content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()
  })
})

describe("DrawerContent - Portal behavior", () => {
  it("should disable portal when portalled is false", () => {
    const { rerender } = render(
      <DrawerContent portalled={false}>
        <div>Content</div>
      </DrawerContent>,
    )
    let content = screen.getByTestId("drawer-content")
    expect(content).toBeInTheDocument()

    rerender(
      <DrawerContent portalled={true}>
        <div>Content</div>
      </DrawerContent>,
    )
    const portal = screen.getByTestId("portal")
    expect(portal).toBeInTheDocument()
  })
})

describe("DrawerCloseTrigger - Props spreading", () => {
  it("should spread all ChakraDrawer.CloseTriggerProps correctly", () => {
    render(
      <DrawerCloseTrigger
        data-test="spreaded"
        onClick={() => {}}
      />,
    )
    const closeTrigger = screen.getByTestId("drawer-close-trigger")
    expect(closeTrigger).toHaveAttribute("data-test", "spreaded")
  })
})