import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import * as React from "react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import {
  DialogContent,
  DialogCloseTrigger,
  DialogRoot,
  DialogFooter,
  DialogHeader,
  DialogBody,
  DialogBackdrop,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogActionTrigger,
} from "./dialog"
import * as ChakraDialog from "@chakra-ui/react"

// Mock Chakra Dialog components
vi.mock("@chakra-ui/react", async () => {
  const actual = await vi.importActual("@chakra-ui/react")
  return {
    ...actual,
    Dialog: {
      Root: ({ children }: any) => <div data-testid="dialog-root">{children}</div>,
      Content: React.forwardRef(({ children, ...props }: any, ref: any) => (
        <div data-testid="dialog-content" ref={ref} {...props}>
          {children}
        </div>
      )),
      Backdrop: () => <div data-testid="dialog-backdrop" />,
      Positioner: ({ children }: any) => (
        <div data-testid="dialog-positioner">{children}</div>
      ),
      CloseTrigger: ({ children, ...props }: any) => (
        <button data-testid="dialog-close-trigger" {...props}>
          {children}
        </button>
      ),
      Footer: ({ children }: any) => <div data-testid="dialog-footer">{children}</div>,
      Header: ({ children }: any) => <div data-testid="dialog-header">{children}</div>,
      Body: ({ children }: any) => <div data-testid="dialog-body">{children}</div>,
      Title: ({ children }: any) => <h2 data-testid="dialog-title">{children}</h2>,
      Description: ({ children }: any) => <p data-testid="dialog-description">{children}</p>,
      Trigger: ({ children }: any) => <button data-testid="dialog-trigger">{children}</button>,
      ActionTrigger: ({ children }: any) => (
        <button data-testid="dialog-action-trigger">{children}</button>
      ),
    },
    Portal: ({ children, disabled, container }: any) =>
      disabled ? (
        children
      ) : (
        <div data-testid="portal" data-disabled={disabled} data-container={container?.current}>
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

describe("DialogContent", () => {
  it("should render with portalled enabled by default", () => {
    render(
      <DialogContent>
        <div>Test Content</div>
      </DialogContent>,
    )
    const portal = screen.getByTestId("portal")
    expect(portal).toBeInTheDocument()
    expect(portal).toHaveAttribute("data-disabled", "false")
  })

  it("should render with portalled disabled when portalled prop is false", () => {
    render(
      <DialogContent portalled={false}>
        <div>Test Content</div>
      </DialogContent>,
    )
    // When disabled, Portal returns children directly, so no portal wrapper
    const content = screen.getByTestId("dialog-content")
    expect(content).toBeInTheDocument()
  })

  it("should render backdrop by default", () => {
    render(
      <DialogContent>
        <div>Test Content</div>
      </DialogContent>,
    )
    const backdrop = screen.getByTestId("dialog-backdrop")
    expect(backdrop).toBeInTheDocument()
  })

  it("should not render backdrop when backdrop prop is false", () => {
    render(
      <DialogContent backdrop={false}>
        <div>Test Content</div>
      </DialogContent>,
    )
    const backdrop = screen.queryByTestId("dialog-backdrop")
    expect(backdrop).not.toBeInTheDocument()
  })

  it("should render positioner and content elements", () => {
    render(
      <DialogContent>
        <div>Test Content</div>
      </DialogContent>,
    )
    const positioner = screen.getByTestId("dialog-positioner")
    const content = screen.getByTestId("dialog-content")
    expect(positioner).toBeInTheDocument()
    expect(content).toBeInTheDocument()
  })

  it("should render children content", () => {
    render(
      <DialogContent>
        <p>Child Content Text</p>
      </DialogContent>,
    )
    expect(screen.getByText("Child Content Text")).toBeInTheDocument()
  })

  it("should forward ref to DialogContent", () => {
    const ref = React.createRef<HTMLDivElement>()
    render(
      <DialogContent ref={ref}>
        <div>Test Content</div>
      </DialogContent>,
    )
    expect(ref.current).toBeTruthy()
  })

  it("should pass through custom props to ChakraDialog.Content", () => {
    const { container } = render(
      <DialogContent data-custom="test-value" className="custom-class">
        <div>Test Content</div>
      </DialogContent>,
    )
    const content = screen.getByTestId("dialog-content")
    expect(content).toHaveAttribute("data-custom", "test-value")
    expect(content).toHaveAttribute("class", expect.stringContaining("custom-class"))
  })

  it("should use custom portalRef when provided", () => {
    const portalRef = React.createRef<HTMLElement>()
    render(
      <DialogContent portalRef={portalRef}>
        <div>Test Content</div>
      </DialogContent>,
    )
    const portal = screen.getByTestId("portal")
    expect(portal).toBeInTheDocument()
  })

  it("should combine multiple props correctly", () => {
    render(
      <DialogContent
        portalled={true}
        backdrop={true}
        data-test="combined"
      >
        <span>Combined Test</span>
      </DialogContent>,
    )
    const backdrop = screen.getByTestId("dialog-backdrop")
    const content = screen.getByTestId("dialog-content")
    expect(backdrop).toBeInTheDocument()
    expect(content).toBeInTheDocument()
    expect(screen.getByText("Combined Test")).toBeInTheDocument()
  })

  it("should set asChild to false on ChakraDialog.Content", () => {
    render(
      <DialogContent>
        <div>Test</div>
      </DialogContent>,
    )
    const content = screen.getByTestId("dialog-content")
    expect(content).toHaveAttribute("asChild", "false")
  })
})

describe("DialogCloseTrigger", () => {
  it("should render close button", () => {
    render(
      <DialogCloseTrigger>
        <span>Close</span>
      </DialogCloseTrigger>,
    )
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton).toBeInTheDocument()
  })

  it("should pass size sm to close button", () => {
    render(<DialogCloseTrigger />)
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton).toHaveAttribute("size", "sm")
  })

  it("should forward ref correctly", () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<DialogCloseTrigger ref={ref} />)
    expect(ref.current).toBeTruthy()
  })

  it("should render children if provided", () => {
    render(
      <DialogCloseTrigger>
        <span>Custom Close Icon</span>
      </DialogCloseTrigger>,
    )
    expect(screen.getByText("Custom Close Icon")).toBeInTheDocument()
  })

  it("should have position absolute with top and insetEnd styles", () => {
    const { container } = render(<DialogCloseTrigger />)
    const closeTrigger = screen.getByTestId("dialog-close-trigger")
    expect(closeTrigger).toHaveAttribute("position", "absolute")
    expect(closeTrigger).toHaveAttribute("top", "2")
    expect(closeTrigger).toHaveAttribute("insetEnd", "2")
  })

  it("should pass through additional props", () => {
    render(
      <DialogCloseTrigger data-testid="custom-close" aria-label="Close dialog" />,
    )
    const closeTrigger = screen.getByTestId("custom-close")
    expect(closeTrigger).toHaveAttribute("aria-label", "Close dialog")
  })

  it("should set asChild to true on ChakraDialog.CloseTrigger", () => {
    const { container } = render(<DialogCloseTrigger />)
    const closeTrigger = screen.getByTestId("dialog-close-trigger")
    expect(closeTrigger).toHaveAttribute("asChild", "true")
  })
})

describe("Dialog exported components", () => {
  it("should export DialogRoot from ChakraDialog.Root", () => {
    expect(DialogRoot).toBeDefined()
    expect(DialogRoot).toBe(ChakraDialog.Root)
  })

  it("should export DialogFooter from ChakraDialog.Footer", () => {
    expect(DialogFooter).toBeDefined()
    expect(DialogFooter).toBe(ChakraDialog.Footer)
  })

  it("should export DialogHeader from ChakraDialog.Header", () => {
    expect(DialogHeader).toBeDefined()
    expect(DialogHeader).toBe(ChakraDialog.Header)
  })

  it("should export DialogBody from ChakraDialog.Body", () => {
    expect(DialogBody).toBeDefined()
    expect(DialogBody).toBe(ChakraDialog.Body)
  })

  it("should export DialogBackdrop from ChakraDialog.Backdrop", () => {
    expect(DialogBackdrop).toBeDefined()
    expect(DialogBackdrop).toBe(ChakraDialog.Backdrop)
  })

  it("should export DialogTitle from ChakraDialog.Title", () => {
    expect(DialogTitle).toBeDefined()
    expect(DialogTitle).toBe(ChakraDialog.Title)
  })

  it("should export DialogDescription from ChakraDialog.Description", () => {
    expect(DialogDescription).toBeDefined()
    expect(DialogDescription).toBe(ChakraDialog.Description)
  })

  it("should export DialogTrigger from ChakraDialog.Trigger", () => {
    expect(DialogTrigger).toBeDefined()
    expect(DialogTrigger).toBe(ChakraDialog.Trigger)
  })

  it("should export DialogActionTrigger from ChakraDialog.ActionTrigger", () => {
    expect(DialogActionTrigger).toBeDefined()
    expect(DialogActionTrigger).toBe(ChakraDialog.ActionTrigger)
  })
})

describe("DialogContent - Edge Cases", () => {
  it("should handle null children", () => {
    const { container } = render(
      <DialogContent>{null}</DialogContent>,
    )
    const content = screen.getByTestId("dialog-content")
    expect(content).toBeInTheDocument()
  })

  it("should handle undefined children", () => {
    const { container } = render(
      <DialogContent>{undefined}</DialogContent>,
    )
    const content = screen.getByTestId("dialog-content")
    expect(content).toBeInTheDocument()
  })

  it("should handle empty string children", () => {
    const { container } = render(
      <DialogContent>{""}</DialogContent>,
    )
    const content = screen.getByTestId("dialog-content")
    expect(content).toBeInTheDocument()
  })

  it("should render with all props set to true", () => {
    render(
      <DialogContent portalled={true} backdrop={true}>
        <div>Content</div>
      </DialogContent>,
    )
    const backdrop = screen.getByTestId("dialog-backdrop")
    expect(backdrop).toBeInTheDocument()
  })

  it("should render with all props set to false", () => {
    render(
      <DialogContent portalled={false} backdrop={false}>
        <div>Content</div>
      </DialogContent>,
    )
    const backdrop = screen.queryByTestId("dialog-backdrop")
    expect(backdrop).not.toBeInTheDocument()
  })

  it("should handle multiple children nodes", () => {
    render(
      <DialogContent>
        <div>First</div>
        <div>Second</div>
        <div>Third</div>
      </DialogContent>,
    )
    expect(screen.getByText("First")).toBeInTheDocument()
    expect(screen.getByText("Second")).toBeInTheDocument()
    expect(screen.getByText("Third")).toBeInTheDocument()
  })
})

describe("DialogCloseTrigger - Edge Cases", () => {
  it("should handle no children", () => {
    const { container } = render(<DialogCloseTrigger />)
    const closeButton = screen.getByTestId("close-button")
    expect(closeButton).toBeInTheDocument()
  })

  it("should handle complex children", () => {
    render(
      <DialogCloseTrigger>
        <svg>
          <circle cx="50" cy="50" r="40" />
        </svg>
      </DialogCloseTrigger>,
    )
    const svg = screen.getByRole("img", { hidden: true })
    expect(svg).toBeInTheDocument()
  })
})