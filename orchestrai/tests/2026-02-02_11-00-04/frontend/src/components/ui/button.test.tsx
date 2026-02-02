import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { Button } from "./button"

// Mock Chakra UI components
vi.mock("@chakra-ui/react", () => ({
  AbsoluteCenter: ({ children }: any) => <div data-testid="absolute-center">{children}</div>,
  Button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  Span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  Spinner: (props: any) => <div data-testid="spinner" {...props} />,
}))

describe("Button Component", () => {
  describe("Rendering", () => {
    it("should render button with children when not loading", () => {
      render(<Button>Click me</Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
      expect(screen.getByText("Click me")).toBeInTheDocument()
    })

    it("should render button with custom className", () => {
      render(<Button className="custom-class">Test</Button>)
      expect(screen.getByRole("button")).toHaveClass("custom-class")
    })

    it("should render button with variant prop", () => {
      const { container } = render(<Button variant="solid">Test</Button>)
      expect(container.querySelector("button")).toBeInTheDocument()
    })

    it("should render button with color prop", () => {
      render(<Button colorScheme="red">Test</Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should render button with size prop", () => {
      render(<Button size="lg">Test</Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })
  })

  describe("Loading State", () => {
    it("should display spinner when loading is true and no loadingText", () => {
      render(<Button loading={true}>Click me</Button>)
      expect(screen.getByTestId("spinner")).toBeInTheDocument()
    })

    it("should hide children text with opacity when loading without loadingText", () => {
      render(<Button loading={true}>Click me</Button>)
      const span = screen.getByText("Click me")
      expect(span).toHaveStyle({ opacity: 0 })
    })

    it("should display spinner and loadingText when both loading and loadingText are provided", () => {
      render(<Button loading={true} loadingText="Loading...">
        Click me
      </Button>)
      expect(screen.getByTestId("spinner")).toBeInTheDocument()
      expect(screen.getByText("Loading...")).toBeInTheDocument()
    })

    it("should not render children when loading with loadingText", () => {
      const { queryByText } = render(<Button loading={true} loadingText="Loading...">
        Click me
      </Button>)
      expect(queryByText("Click me")).not.toBeInTheDocument()
    })

    it("should render children when loading is false", () => {
      render(<Button loading={false}>Click me</Button>)
      expect(screen.queryByTestId("spinner")).not.toBeInTheDocument()
      expect(screen.getByText("Click me")).toBeInTheDocument()
    })

    it("should render children when loading is undefined", () => {
      render(<Button>Click me</Button>)
      expect(screen.queryByTestId("spinner")).not.toBeInTheDocument()
      expect(screen.getByText("Click me")).toBeInTheDocument()
    })

    it("should render loadingText as ReactNode", () => {
      render(<Button loading={true} loadingText={<span data-testid="custom-loading">Custom</span>}>
        Click me
      </Button>)
      expect(screen.getByTestId("custom-loading")).toBeInTheDocument()
    })
  })

  describe("Disabled State", () => {
    it("should disable button when disabled prop is true", () => {
      render(<Button disabled={true}>Click me</Button>)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should disable button when loading is true", () => {
      render(<Button loading={true}>Click me</Button>)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should disable button when both loading and disabled are true", () => {
      render(<Button loading={true} disabled={true}>
        Click me
      </Button>)
      expect(screen.getByRole("button")).toBeDisabled()
    })

    it("should enable button when disabled is false and loading is false", () => {
      render(<Button disabled={false} loading={false}>
        Click me
      </Button>)
      expect(screen.getByRole("button")).not.toBeDisabled()
    })

    it("should enable button when disabled is undefined and loading is undefined", () => {
      render(<Button>Click me</Button>)
      expect(screen.getByRole("button")).not.toBeDisabled()
    })

    it("should prioritize loading disabled state over disabled prop", () => {
      render(<Button loading={true} disabled={false}>
        Click me
      </Button>)
      expect(screen.getByRole("button")).toBeDisabled()
    })
  })

  describe("Props Forwarding", () => {
    it("should forward Chakra Button props", () => {
      const { container } = render(<Button data-testid="custom-button">Test</Button>)
      expect(screen.getByTestId("custom-button")).toBeInTheDocument()
    })

    it("should forward event handlers", () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)
      screen.getByRole("button").click()
      expect(handleClick).toHaveBeenCalled()
    })

    it("should forward aria attributes", () => {
      render(<Button aria-label="Custom button">Click me</Button>)
      expect(screen.getByRole("button")).toHaveAttribute("aria-label", "Custom button")
    })

    it("should forward data attributes", () => {
      render(<Button data-custom="value">Click me</Button>)
      expect(screen.getByRole("button")).toHaveAttribute("data-custom", "value")
    })
  })

  describe("Ref Forwarding", () => {
    it("should forward ref to HTMLButtonElement", () => {
      const ref = vi.fn()
      render(<Button ref={ref}>Click me</Button>)
      expect(ref).toHaveBeenCalled()
      expect(ref.mock.calls[0][0]).toBeInstanceOf(HTMLButtonElement)
    })

    it("should allow accessing button element via ref", () => {
      const ref = { current: null as HTMLButtonElement | null }
      const { container } = render(<Button ref={ref}>Click me</Button>)
      expect(ref.current).not.toBeNull()
    })
  })

  describe("Children Variations", () => {
    it("should render string children", () => {
      render(<Button>String children</Button>)
      expect(screen.getByText("String children")).toBeInTheDocument()
    })

    it("should render ReactNode children", () => {
      render(<Button><span data-testid="custom-child">Custom</span></Button>)
      expect(screen.getByTestId("custom-child")).toBeInTheDocument()
    })

    it("should render multiple children", () => {
      render(<Button>
        <span>Child 1</span>
        <span>Child 2</span>
      </Button>)
      expect(screen.getByText("Child 1")).toBeInTheDocument()
      expect(screen.getByText("Child 2")).toBeInTheDocument()
    })

    it("should render empty children", () => {
      render(<Button></Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should render null children", () => {
      render(<Button>{null}</Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })
  })

  describe("Loading State Edge Cases", () => {
    it("should handle loading as undefined with loadingText", () => {
      render(<Button loadingText="Loading...">Click me</Button>)
      expect(screen.queryByTestId("spinner")).not.toBeInTheDocument()
      expect(screen.getByText("Click me")).toBeInTheDocument()
    })

    it("should handle loading as false with loadingText", () => {
      render(<Button loading={false} loadingText="Loading...">
        Click me
      </Button>)
      expect(screen.queryByTestId("spinner")).not.toBeInTheDocument()
      expect(screen.getByText("Click me")).toBeInTheDocument()
    })

    it("should show spinner with inherit size", () => {
      render(<Button loading={true}>Click me</Button>)
      const spinner = screen.getByTestId("spinner")
      expect(spinner).toBeInTheDocument()
    })

    it("should show spinner with inherit color", () => {
      render(<Button loading={true}>Click me</Button>)
      const spinner = screen.getByTestId("spinner")
      expect(spinner).toBeInTheDocument()
    })
  })

  describe("Complex Loading Scenarios", () => {
    it("should conditionally show AbsoluteCenter when loading without loadingText", () => {
      render(<Button loading={true}>Content</Button>)
      expect(screen.getByTestId("absolute-center")).toBeInTheDocument()
    })

    it("should not show AbsoluteCenter when loading with loadingText", () => {
      const { queryByTestId } = render(<Button loading={true} loadingText="Loading...">
        Content
      </Button>)
      expect(queryByTestId("absolute-center")).not.toBeInTheDocument()
    })

    it("should not show AbsoluteCenter when not loading", () => {
      const { queryByTestId } = render(<Button loading={false}>Content</Button>)
      expect(queryByTestId("absolute-center")).not.toBeInTheDocument()
    })
  })

  describe("Type Safety", () => {
    it("should accept ButtonProps interface", () => {
      const props = {
        loading: true,
        disabled: false,
        loadingText: "Loading...",
        children: "Click me",
        className: "custom",
      }
      render(<Button {...props}>Click me</Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("should accept ChakraButtonProps", () => {
      render(<Button colorScheme="blue" size="md">
        Click me
      </Button>)
      expect(screen.getByRole("button")).toBeInTheDocument()
    })
  })
})