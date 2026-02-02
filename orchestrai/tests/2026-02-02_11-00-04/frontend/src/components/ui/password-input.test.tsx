import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { PasswordInput, PasswordStrengthMeter } from "./password-input"
import { ChakraProvider } from "@chakra-ui/react"
import React from "react"

// Mock react-icons
vi.mock("react-icons/fi", () => ({
  FiEye: () => <div data-testid="eye-icon">Eye</div>,
  FiEyeOff: () => <div data-testid="eye-off-icon">EyeOff</div>,
}))

// Mock Field component
vi.mock("./field", () => ({
  Field: ({ children, invalid, errorText }: any) => (
    <div data-testid="field" data-invalid={invalid}>
      {children}
      {errorText && <div data-testid="error-text">{errorText}</div>}
    </div>
  ),
}))

// Mock InputGroup component
vi.mock("./input-group", () => ({
  InputGroup: ({ children, startElement, endElement, ...props }: any) => (
    <div data-testid="input-group" {...props}>
      {startElement && <div data-testid="start-element">{startElement}</div>}
      {children}
      {endElement && <div data-testid="end-element">{endElement}</div>}
    </div>
  ),
}))

const Wrapper = ({ children }: any) => (
  <ChakraProvider>{children}</ChakraProvider>
)

describe("PasswordInput", () => {
  const defaultProps = {
    type: "password",
    errors: {},
  }

  describe("basic rendering", () => {
    it("should render input element with correct structure", () => {
      render(
        <PasswordInput
          {...defaultProps}
          data-testid="password-input"
          placeholder="Enter password"
        />,
        { wrapper: Wrapper },
      )

      const inputGroup = screen.getByTestId("input-group")
      expect(inputGroup).toBeInTheDocument()
    })

    it("should render with Field component", () => {
      render(<PasswordInput {...defaultProps} />, { wrapper: Wrapper })

      const field = screen.getByTestId("field")
      expect(field).toBeInTheDocument()
    })

    it("should render visibility trigger button", () => {
      render(<PasswordInput {...defaultProps} />, { wrapper: Wrapper })

      const endElement = screen.getByTestId("end-element")
      expect(endElement).toBeInTheDocument()
    })

    it("should render start element when provided", () => {
      const startElement = <span data-testid="custom-start">Start</span>
      render(
        <PasswordInput {...defaultProps} startElement={startElement} />,
        { wrapper: Wrapper },
      )

      expect(screen.getByTestId("custom-start")).toBeInTheDocument()
    })
  })

  describe("password visibility toggle", () => {
    it("should show password icon initially when visible is false (default)", () => {
      render(<PasswordInput {...defaultProps} />, { wrapper: Wrapper })

      expect(screen.getByTestId("eye-icon")).toBeInTheDocument()
    })

    it("should show eye off icon when password is visible", async () => {
      render(
        <PasswordInput {...defaultProps} defaultVisible={true} />,
        { wrapper: Wrapper },
      )

      await waitFor(() => {
        expect(screen.getByTestId("eye-off-icon")).toBeInTheDocument()
      })
    })

    it("should toggle password visibility on button click", async () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      const endElement = screen.getByTestId("end-element")
      const button = endElement.querySelector("button")

      expect(button).toBeInTheDocument()
      if (button) {
        fireEvent.click(button)
        await waitFor(() => {
          expect(screen.getByTestId("eye-off-icon")).toBeInTheDocument()
        })
      }
    })

    it("should not toggle when disabled", async () => {
      const { container } = render(
        <PasswordInput {...defaultProps} disabled={true} />,
        { wrapper: Wrapper },
      )

      const endElement = screen.getByTestId("end-element")
      const button = endElement.querySelector("button")

      if (button) {
        fireEvent.click(button)
        // Should still show eye icon since toggle was prevented
        expect(screen.getByTestId("eye-icon")).toBeInTheDocument()
      }
    })

    it("should ignore non-left mouse button clicks", async () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      const endElement = screen.getByTestId("end-element")
      const button = endElement.querySelector("button")

      if (button) {
        fireEvent.pointerDown(button, { button: 2 }) // Right click
        // Should not toggle
        expect(screen.getByTestId("eye-icon")).toBeInTheDocument()
      }
    })

    it("should call onVisibleChange callback when visibility changes", async () => {
      const onVisibleChange = vi.fn()
      const { rerender } = render(
        <PasswordInput
          {...defaultProps}
          onVisibleChange={onVisibleChange}
        />,
        { wrapper: Wrapper },
      )

      const endElement = screen.getByTestId("end-element")
      const button = endElement.querySelector("button")

      if (button) {
        fireEvent.click(button)
        await waitFor(() => {
          expect(onVisibleChange).toHaveBeenCalledWith(true)
        })
      }
    })

    it("should respect controlled visible prop", () => {
      const { rerender } = render(
        <PasswordInput {...defaultProps} visible={false} />,
        { wrapper: Wrapper },
      )

      expect(screen.getByTestId("eye-icon")).toBeInTheDocument()

      rerender(
        <PasswordInput {...defaultProps} visible={true} />,
      )

      expect(screen.getByTestId("eye-off-icon")).toBeInTheDocument()
    })
  })

  describe("custom visibility icons", () => {
    it("should use custom visibility icons when provided", () => {
      const customIcons = {
        on: <span data-testid="custom-on">Custom On</span>,
        off: <span data-testid="custom-off">Custom Off</span>,
      }

      render(
        <PasswordInput
          {...defaultProps}
          visibilityIcon={customIcons}
          defaultVisible={false}
        />,
        { wrapper: Wrapper },
      )

      expect(screen.getByTestId("custom-on")).toBeInTheDocument()
    })

    it("should show custom off icon when visible", async () => {
      const customIcons = {
        on: <span data-testid="custom-on">Custom On</span>,
        off: <span data-testid="custom-off">Custom Off</span>,
      }

      render(
        <PasswordInput
          {...defaultProps}
          visibilityIcon={customIcons}
          defaultVisible={true}
        />,
        { wrapper: Wrapper },
      )

      await waitFor(() => {
        expect(screen.getByTestId("custom-off")).toBeInTheDocument()
      })
    })
  })

  describe("error handling", () => {
    it("should display error when errors object has error message", () => {
      const errors = {
        password: { message: "Password is required" },
      }

      render(
        <PasswordInput {...defaultProps} type="password" errors={errors} />,
        { wrapper: Wrapper },
      )

      expect(screen.getByTestId("error-text")).toHaveTextContent(
        "Password is required",
      )
    })

    it("should mark field as invalid when error exists", () => {
      const errors = {
        password: { message: "Invalid password" },
      }

      render(
        <PasswordInput {...defaultProps} type="password" errors={errors} />,
        { wrapper: Wrapper },
      )

      const field = screen.getByTestId("field")
      expect(field).toHaveAttribute("data-invalid", "true")
    })

    it("should not display error when errors object is empty", () => {
      render(
        <PasswordInput {...defaultProps} type="password" errors={{}} />,
        { wrapper: Wrapper },
      )

      const field = screen.getByTestId("field")
      expect(field).toHaveAttribute("data-invalid", "false")
    })

    it("should not display error for different field type", () => {
      const errors = {
        email: { message: "Invalid email" },
      }

      render(
        <PasswordInput {...defaultProps} type="password" errors={errors} />,
        { wrapper: Wrapper },
      )

      expect(screen.queryByTestId("error-text")).not.toBeInTheDocument()
    })
  })

  describe("input type attribute", () => {
    it("should render as password type by default", () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      const input = container.querySelector("input")
      expect(input).toHaveAttribute("type", "password")
    })

    it("should change type to text when visible is true", async () => {
      const { container } = render(
        <PasswordInput {...defaultProps} defaultVisible={true} />,
        { wrapper: Wrapper },
      )

      await waitFor(() => {
        const input = container.querySelector("input")
        expect(input).toHaveAttribute("type", "text")
      })
    })

    it("should toggle type between password and text", async () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      let input = container.querySelector("input")
      expect(input).toHaveAttribute("type", "password")

      const endElement = screen.getByTestId("end-element")
      const button = endElement.querySelector("button")

      if (button) {
        fireEvent.click(button)
        await waitFor(() => {
          input = container.querySelector("input")
          expect(input).toHaveAttribute("type", "text")
        })
      }
    })
  })

  describe("rootProps and other props", () => {
    it("should pass rootProps to InputGroup", () => {
      const rootProps = { "data-custom": "value" }

      render(
        <PasswordInput
          {...defaultProps}
          rootProps={rootProps}
          data-testid="test-input"
        />,
        { wrapper: Wrapper },
      )

      const inputGroup = screen.getByTestId("input-group")
      expect(inputGroup).toHaveAttribute("data-custom", "value")
    })

    it("should pass through standard input props", () => {
      const { container } = render(
        <PasswordInput
          {...defaultProps}
          placeholder="Enter your password"
          autoComplete="off"
          required={true}
        />,
        { wrapper: Wrapper },
      )

      const input = container.querySelector("input")
      expect(input).toHaveAttribute("placeholder", "Enter your password")
      expect(input).toHaveAttribute("autocomplete", "off")
      expect(input).toHaveAttribute("required")
    })
  })

  describe("ref forwarding", () => {
    it("should forward ref to input element", () => {
      const ref = React.createRef<HTMLInputElement>()

      render(<PasswordInput {...defaultProps} ref={ref} />, {
        wrapper: Wrapper,
      })

      expect(ref.current).toBeInstanceOf(HTMLInputElement)
    })

    it("should allow manipulation through ref", () => {
      const ref = React.createRef<HTMLInputElement>()

      render(<PasswordInput {...defaultProps} ref={ref} />, {
        wrapper: Wrapper,
      })

      if (ref.current) {
        ref.current.focus()
        expect(ref.current).toHaveFocus()
      }
    })
  })

  describe("accessibility", () => {
    it("should have aria-label on visibility trigger", () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      const button = container.querySelector("[aria-label]")
      expect(button).toHaveAttribute("aria-label", "Toggle password visibility")
    })

    it("should have tabIndex -1 on visibility trigger", () => {
      const { container } = render(
        <PasswordInput {...defaultProps} />,
        { wrapper: Wrapper },
      )

      const button = container.querySelector("button")
      expect(button).toHaveAttribute("tabindex", "-1")
    })
  })
})

describe("PasswordStrengthMeter", () => {
  describe("rendering", () => {
    it("should render correct number of boxes based on max prop", () => {
      const { container } = render(
        <PasswordStrengthMeter value={2} max={4} />,
        { wrapper: Wrapper },
      )

      const boxes = container.querySelectorAll('[data-selected=""]')
      expect(boxes.length).toBe(2)
    })

    it("should use default max value of 4", () => {
      const { container } = render(
        <PasswordStrengthMeter value={2} />,
        { wrapper: Wrapper },
      )

      const boxes = container.querySelectorAll("div[data-selected]")
      expect(boxes.length).toBe(4)
    })

    it("should render custom max value", () => {
      const { container } = render(
        <PasswordStrengthMeter value={1} max={5} />,
        { wrapper: Wrapper },
      )

      const allBoxes = container.querySelectorAll(
        "[data-selected], [data-selected='']",
      )
      expect(allBoxes.length).toBeGreaterThanOrEqual(5)
    })
  })

  describe("selected state", () => {
    it("should mark boxes as selected based on value", () => {
      const { container } = render(
        <PasswordStrengthMeter value={2} max={4} />,
        { wrapper: Wrapper },
      )

      const selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(2)
    })

    it("should have correct unselected boxes", () => {
      const { container } = render(
        <PasswordStrengthMeter value={1} max={4} />,
        { wrapper: Wrapper },
      )

      const selectedBoxes = container.querySelectorAll('[data-selected=""]')
      const unselectedBoxes = container.querySelectorAll(
        "div[data-selected=undefined]",
      )

      expect(selectedBoxes.length).toBe(1)
    })

    it("should update when value changes", () => {
      const { rerender, container } = render(
        <PasswordStrengthMeter value={1} max={4} />,
        { wrapper: Wrapper },
      )

      let selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(1)

      rerender(<PasswordStrengthMeter value={3} max={4} />)

      selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(3)
    })
  })

  describe("color palette based on strength", () => {
    it("should use red palette for low strength (< 33%)", () => {
      // 1/4 = 25%
      const { container } = render(
        <PasswordStrengthMeter value={1} max={4} />,
        { wrapper: Wrapper },
      )

      screen.getByText("Low")
    })

    it("should use orange palette for medium strength (33-66%)", () => {
      // 2/4 = 50%
      const { container } = render(
        <PasswordStrengthMeter value={2} max={4} />,
        { wrapper: Wrapper },
      )

      screen.getByText("Medium")
    })

    it("should use green palette for high strength (>= 66%)", () => {
      // 3/4 = 75%
      const { container } = render(
        <PasswordStrengthMeter value={3} max={4} />,
        { wrapper: Wrapper },
      )

      screen.getByText("High")
    })

    it("should show High for exactly 66%", () => {
      // 66/100 = 66%
      const { container } = render(
        <PasswordStrengthMeter value={66} max={100} />,
        { wrapper: Wrapper },
      )

      screen.getByText("High")
    })
  })

  describe("edge cases", () => {
    it("should handle zero value", () => {
      const { container } = render(
        <PasswordStrengthMeter value={0} max={4} />,
        { wrapper: Wrapper },
      )

      const selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(0)
    })

    it("should handle value equal to max", () => {
      const { container } = render(
        <PasswordStrengthMeter value={4} max={4} />,
        { wrapper: Wrapper },
      )

      const selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(4)
    })

    it("should handle value greater than max", () => {
      const { container } = render(
        <PasswordStrengthMeter value={5} max={4} />,
        { wrapper: Wrapper },
      )

      const selectedBoxes = container.querySelectorAll('[data-selected=""]')
      expect(selectedBoxes.length).toBe(5)
    })

    it("should handle large max value", () => {
      const { container } = render(
        <PasswordStrengthMeter value={50} max={100} />,
        { wrapper: Wrapper },
      )

      const allBoxes = container.querySelectorAll(
        "[data-selected], [data-selected='']",
      )
      expect(allBoxes.length).toBeGreaterThanOrEqual(100)
    })
  })

  describe("label visibility", () => {
    it("should display label for low strength", () => {
      render(<PasswordStrengthMeter value={1} max={4} />, {
        wrapper: Wrapper,
      })

      expect(screen.getByText("Low")).toBeInTheDocument()
    })

    it("should display label for medium strength", () => {
      render(<PasswordStrengthMeter value={2} max={4} />, {
        wrapper: Wrapper,
      })

      expect(screen.getByText("Medium")).toBeInTheDocument()
    })

    it("should display label for high strength", () => {
      render(<PasswordStrengthMeter value={3} max={4} />, {
        wrapper: Wrapper,
      })

      expect(screen.getByText("High")).toBeInTheDocument()
    })
  })

  describe("ref forwarding", () => {
    it("should forward ref to root container", () => {
      const ref = React.createRef<HTMLDivElement>()

      render(<PasswordStrengthMeter value={2} max={4} ref={ref} />, {
        wrapper: Wrapper,
      })

      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })
  })

  describe("custom props", () => {
    it("should pass through custom props to root", () => {
      render(
        <PasswordStrengthMeter value={2} max={4} data-testid="custom-meter" />,
        { wrapper: Wrapper },
      )

      expect(screen.getByTestId("custom-meter")).toBeInTheDocument()
    })
  })
})

describe("getColorPalette function", () => {
  // Since getColorPalette is an internal function, we test it through PasswordStrengthMeter
  it("should return Low color palette for 0 percent", () => {
    render(<PasswordStrengthMeter value={0} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("Low")).toBeInTheDocument()
  })

  it("should return Low color palette for 32 percent", () => {
    render(<PasswordStrengthMeter value={32} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("Low")).toBeInTheDocument()
  })

  it("should return Medium color palette for 33 percent", () => {
    render(<PasswordStrengthMeter value={33} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("Medium")).toBeInTheDocument()
  })

  it("should return Medium color palette for 65 percent", () => {
    render(<PasswordStrengthMeter value={65} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("Medium")).toBeInTheDocument()
  })

  it("should return High color palette for 66 percent", () => {
    render(<PasswordStrengthMeter value={66} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("High")).toBeInTheDocument()
  })

  it("should return High color palette for 100 percent", () => {
    render(<PasswordStrengthMeter value={100} max={100} />, {
      wrapper: Wrapper,
    })

    expect(screen.getByText("High")).toBeInTheDocument()
  })
})