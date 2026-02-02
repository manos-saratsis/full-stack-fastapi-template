import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { Checkbox } from "./checkbox"

// Mock Chakra UI Checkbox components
vi.mock("@chakra-ui/react", () => ({
  Checkbox: {
    Root: ({ children, ref, ...props }: any) => (
      <label data-testid="checkbox-root" {...props} ref={ref}>
        {children}
      </label>
    ),
    HiddenInput: ({ ref, ...props }: any) => (
      <input ref={ref} type="checkbox" data-testid="checkbox-input" {...props} />
    ),
    Control: ({ children }: any) => (
      <div data-testid="checkbox-control">{children}</div>
    ),
    Indicator: () => <div data-testid="checkbox-indicator" />,
    Label: ({ children }: any) => (
      <span data-testid="checkbox-label">{children}</span>
    ),
  },
}))

describe("Checkbox Component", () => {
  describe("Rendering", () => {
    it("should render checkbox without label", () => {
      render(<Checkbox />)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should render checkbox with label", () => {
      render(<Checkbox>Accept terms</Checkbox>)
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("Accept terms")
    })

    it("should render checkbox with children as null", () => {
      render(<Checkbox>{null}</Checkbox>)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should render checkbox with children as undefined", () => {
      render(<Checkbox>{undefined}</Checkbox>)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should render checkbox with empty string children", () => {
      render(<Checkbox>{""}</Checkbox>)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should render checkbox control element", () => {
      render(<Checkbox />)
      expect(screen.getByTestId("checkbox-control")).toBeInTheDocument()
    })

    it("should render checkbox root element", () => {
      render(<Checkbox />)
      expect(screen.getByTestId("checkbox-root")).toBeInTheDocument()
    })
  })

  describe("Icon Prop", () => {
    it("should render custom icon when provided", () => {
      render(<Checkbox icon={<div data-testid="custom-icon">✓</div>} />)
      expect(screen.getByTestId("custom-icon")).toBeInTheDocument()
    })

    it("should render default indicator when icon not provided", () => {
      render(<Checkbox />)
      expect(screen.getByTestId("checkbox-indicator")).toBeInTheDocument()
    })

    it("should not render indicator when custom icon is provided", () => {
      const { queryByTestId } = render(
        <Checkbox icon={<div data-testid="custom-icon">✓</div>} />
      )
      expect(queryByTestId("checkbox-indicator")).not.toBeInTheDocument()
    })

    it("should render ReactNode as icon", () => {
      render(
        <Checkbox
          icon={
            <svg data-testid="svg-icon">
              <circle />
            </svg>
          }
        />
      )
      expect(screen.getByTestId("svg-icon")).toBeInTheDocument()
    })

    it("should render icon with null value", () => {
      render(<Checkbox icon={null} />)
      expect(screen.getByTestId("checkbox-indicator")).toBeInTheDocument()
    })

    it("should render icon with undefined value", () => {
      render(<Checkbox icon={undefined} />)
      expect(screen.getByTestId("checkbox-indicator")).toBeInTheDocument()
    })
  })

  describe("Input Props", () => {
    it("should forward inputProps to hidden input", () => {
      render(<Checkbox inputProps={{ "data-testid": "custom-input" }} />)
      expect(screen.getByTestId("custom-input")).toBeInTheDocument()
    })

    it("should apply name attribute via inputProps", () => {
      render(<Checkbox inputProps={{ name: "agree" }} />)
      expect(screen.getByTestId("checkbox-input")).toHaveAttribute("name", "agree")
    })

    it("should apply value attribute via inputProps", () => {
      render(<Checkbox inputProps={{ value: "yes" }} />)
      expect(screen.getByTestId("checkbox-input")).toHaveAttribute("value", "yes")
    })

    it("should apply disabled attribute via inputProps", () => {
      render(<Checkbox inputProps={{ disabled: true }} />)
      expect(screen.getByTestId("checkbox-input")).toBeDisabled()
    })

    it("should apply required attribute via inputProps", () => {
      render(<Checkbox inputProps={{ required: true }} />)
      expect(screen.getByTestId("checkbox-input")).toBeRequired()
    })

    it("should forward onChange handler via inputProps", async () => {
      const user = userEvent.setup()
      const handleChange = vi.fn()
      render(<Checkbox inputProps={{ onChange: handleChange }} />)
      const input = screen.getByTestId("checkbox-input") as HTMLInputElement
      await user.click(input)
      expect(handleChange).toHaveBeenCalled()
    })

    it("should handle multiple inputProps", () => {
      render(
        <Checkbox
          inputProps={{
            name: "terms",
            value: "accepted",
            disabled: true,
            required: true,
          }}
        />
      )
      const input = screen.getByTestId("checkbox-input")
      expect(input).toHaveAttribute("name", "terms")
      expect(input).toHaveAttribute("value", "accepted")
      expect(input).toBeDisabled()
      expect(input).toBeRequired()
    })

    it("should handle empty inputProps object", () => {
      render(<Checkbox inputProps={{}} />)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should handle undefined inputProps", () => {
      render(<Checkbox inputProps={undefined} />)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })
  })

  describe("Root Ref", () => {
    it("should forward ref to Root element", () => {
      const ref = vi.fn()
      render(<Checkbox rootRef={ref} />)
      expect(ref).toHaveBeenCalled()
    })

    it("should provide access to root element via ref", () => {
      const ref = { current: null as HTMLLabelElement | null }
      render(<Checkbox rootRef={ref} />)
      expect(ref.current).not.toBeNull()
      expect(ref.current?.tagName).toBe("LABEL")
    })

    it("should handle null rootRef", () => {
      render(<Checkbox rootRef={null} />)
      expect(screen.getByTestId("checkbox-root")).toBeInTheDocument()
    })

    it("should handle undefined rootRef", () => {
      render(<Checkbox rootRef={undefined} />)
      expect(screen.getByTestId("checkbox-root")).toBeInTheDocument()
    })
  })

  describe("Input Ref", () => {
    it("should forward ref to HiddenInput element", () => {
      const ref = { current: null as HTMLInputElement | null }
      render(<Checkbox ref={ref} />)
      expect(ref.current).not.toBeNull()
      expect(ref.current?.type).toBe("checkbox")
    })

    it("should allow accessing input element via ref", () => {
      const ref = vi.fn()
      render(<Checkbox ref={ref} />)
      expect(ref).toHaveBeenCalled()
      const inputElement = ref.mock.calls[0][0]
      expect(inputElement?.type).toBe("checkbox")
    })
  })

  describe("Children Variations", () => {
    it("should render string children", () => {
      render(<Checkbox>String label</Checkbox>)
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("String label")
    })

    it("should render ReactNode children", () => {
      render(<Checkbox><strong>Bold label</strong></Checkbox>)
      expect(screen.getByTestId("checkbox-label").querySelector("strong")).toBeInTheDocument()
    })

    it("should render children with HTML entities", () => {
      render(<Checkbox>Terms &amp; Conditions</Checkbox>)
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("Terms & Conditions")
    })

    it("should render numeric children", () => {
      render(<Checkbox>{123}</Checkbox>)
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("123")
    })

    it("should render false as no label", () => {
      const { queryByTestId } = render(<Checkbox>{false}</Checkbox>)
      expect(queryByTestId("checkbox-label")).not.toBeInTheDocument()
    })

    it("should render zero as no label", () => {
      const { queryByTestId } = render(<Checkbox>{0}</Checkbox>)
      expect(queryByTestId("checkbox-label")).not.toBeInTheDocument()
    })
  })

  describe("Root Props", () => {
    it("should forward ChakraCheckbox.RootProps to Root", () => {
      render(<Checkbox data-testid="custom-root" />)
      expect(screen.getByTestId("custom-root")).toBeInTheDocument()
    })

    it("should forward className to Root", () => {
      render(<Checkbox className="custom-class" />)
      expect(screen.getByTestId("checkbox-root")).toHaveClass("custom-class")
    })

    it("should forward custom data attributes", () => {
      render(<Checkbox data-custom="value" />)
      expect(screen.getByTestId("checkbox-root")).toHaveAttribute("data-custom", "value")
    })

    it("should forward aria attributes", () => {
      render(<Checkbox aria-label="Accept terms" />)
      expect(screen.getByTestId("checkbox-root")).toHaveAttribute("aria-label", "Accept terms")
    })
  })

  describe("Complex Scenarios", () => {
    it("should render complete checkbox with all props", () => {
      const handleChange = vi.fn()
      render(
        <Checkbox
          icon={<div data-testid="custom-icon">✓</div>}
          inputProps={{ name: "terms", onChange: handleChange }}
          rootRef={undefined}
          className="custom-checkbox"
        >
          Accept terms and conditions
        </Checkbox>
      )
      expect(screen.getByTestId("custom-icon")).toBeInTheDocument()
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("Accept terms and conditions")
      expect(screen.getByTestId("checkbox-input")).toHaveAttribute("name", "terms")
    })

    it("should render disabled checkbox with label", () => {
      render(
        <Checkbox inputProps={{ disabled: true }}>
          Disabled option
        </Checkbox>
      )
      expect(screen.getByTestId("checkbox-input")).toBeDisabled()
      expect(screen.getByTestId("checkbox-label")).toHaveTextContent("Disabled option")
    })

    it("should render required checkbox with custom icon", () => {
      render(
        <Checkbox
          inputProps={{ required: true }}
          icon={<span data-testid="star">*</span>}
        >
          Required field
        </Checkbox>
      )
      expect(screen.getByTestId("checkbox-input")).toBeRequired()
      expect(screen.getByTestId("star")).toBeInTheDocument()
    })

    it("should render multiple checkboxes with different props", () => {
      const { container } = render(
        <>
          <Checkbox name="option1">Option 1</Checkbox>
          <Checkbox name="option2">Option 2</Checkbox>
        </>
      )
      expect(container.querySelectorAll('[data-testid="checkbox-root"]')).toHaveLength(2)
    })
  })

  describe("Null/Undefined Handling", () => {
    it("should handle null icon gracefully", () => {
      render(<Checkbox icon={null} />)
      expect(screen.getByTestId("checkbox-indicator")).toBeInTheDocument()
    })

    it("should handle undefined icon gracefully", () => {
      render(<Checkbox icon={undefined} />)
      expect(screen.getByTestId("checkbox-indicator")).toBeInTheDocument()
    })

    it("should handle null children gracefully", () => {
      render(<Checkbox>{null}</Checkbox>)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should handle undefined children gracefully", () => {
      render(<Checkbox>{undefined}</Checkbox>)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })

    it("should handle null inputProps gracefully", () => {
      render(<Checkbox inputProps={null as any} />)
      expect(screen.getByTestId("checkbox-input")).toBeInTheDocument()
    })
  })
})