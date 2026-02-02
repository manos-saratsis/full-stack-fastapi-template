import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { BrowserRouter } from "react-router-dom"
import Navbar from "./Navbar"

// Mock chakra-ui hooks
vi.mock("@chakra-ui/react", async () => {
  const actual = await vi.importActual("@chakra-ui/react")
  return {
    ...actual,
    useBreakpointValue: vi.fn(),
  }
})

// Mock components
vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}))

vi.mock("./UserMenu", () => ({
  default: () => <div data-testid="user-menu-component">UserMenu</div>,
}))

import { useBreakpointValue } from "@chakra-ui/react"

describe("Navbar", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should render navbar with flex display on md and above", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    render(<Navbar />)

    const navbar = screen.getByRole("link")
    expect(navbar).toBeInTheDocument()
  })

  it("should render navbar with none display on mobile", () => {
    ;(useBreakpointValue as any).mockReturnValue("none")

    const { container } = render(<Navbar />)

    const flex = container.querySelector('[style*="display"]')
    expect(flex).toHaveStyle("display: none")
  })

  it("should render logo image with correct attributes", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    render(<Navbar />)

    const logo = screen.getByAltText("Logo")
    expect(logo).toBeInTheDocument()
    expect(logo).toHaveAttribute("src", expect.stringContaining("fastapi-logo"))
  })

  it("should render link to home page", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    render(<Navbar />)

    const homeLink = screen.getByRole("link")
    expect(homeLink).toHaveAttribute("href", "/")
  })

  it("should render UserMenu component", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    render(<Navbar />)

    const userMenu = screen.getByTestId("user-menu-component")
    expect(userMenu).toBeInTheDocument()
  })

  it("should have sticky positioning", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    const { container } = render(<Navbar />)

    const flex = container.firstChild
    expect(flex).toHaveStyle("position: sticky")
  })

  it("should have correct styling props", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    const { container } = render(<Navbar />)

    const flex = container.firstChild
    expect(flex).toHaveStyle("justify-content: space-between")
    expect(flex).toHaveStyle("color: white")
    expect(flex).toHaveStyle("align-items: center")
    expect(flex).toHaveStyle("top: 0")
  })

  it("should use useBreakpointValue hook with correct parameters", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    render(<Navbar />)

    expect(useBreakpointValue).toHaveBeenCalledWith({
      base: "none",
      md: "flex",
    })
  })

  it("should handle undefined breakpoint value", () => {
    ;(useBreakpointValue as any).mockReturnValue(undefined)

    const { container } = render(<Navbar />)

    expect(container).toBeTruthy()
  })

  it("should have full width", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    const { container } = render(<Navbar />)

    const flex = container.firstChild
    expect(flex).toHaveStyle("width: 100%")
  })

  it("should have bg.muted background color", () => {
    ;(useBreakpointValue as any).mockReturnValue("flex")

    const { container } = render(<Navbar />)

    const flex = container.firstChild as HTMLElement
    expect(flex).toHaveStyle("background-color: var(--chakra-colors-bg-muted)")
  })
})