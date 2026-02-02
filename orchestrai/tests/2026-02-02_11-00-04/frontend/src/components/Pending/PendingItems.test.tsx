import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import PendingItems from './PendingItems'

// Mock Chakra UI components
vi.mock('@chakra-ui/react', () => ({
  Table: {
    Root: ({ children, size }: any) => (
      <div data-testid="table-root" data-size={JSON.stringify(size)}>
        {children}
      </div>
    ),
    Header: ({ children }: any) => (
      <div data-testid="table-header">{children}</div>
    ),
    Body: ({ children }: any) => (
      <div data-testid="table-body">{children}</div>
    ),
    Row: ({ children, key }: any) => (
      <div data-testid="table-row" key={key}>
        {children}
      </div>
    ),
    Cell: ({ children }: any) => (
      <div data-testid="table-cell">{children}</div>
    ),
    ColumnHeader: ({ children, w }: any) => (
      <div data-testid="table-column-header" data-width={w}>
        {children}
      </div>
    ),
  },
}))

vi.mock('../ui/skeleton', () => ({
  SkeletonText: ({ noOfLines }: any) => (
    <div data-testid="skeleton-text" data-nooflines={noOfLines}>
      Skeleton
    </div>
  ),
}))

describe('PendingItems Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    it('should render the component successfully', () => {
      render(<PendingItems />)
      const tableRoot = screen.getByTestId('table-root')
      expect(tableRoot).toBeInTheDocument()
    })

    it('should render Table.Root with correct size props', () => {
      render(<PendingItems />)
      const tableRoot = screen.getByTestId('table-root')
      const sizeProps = tableRoot.getAttribute('data-size')
      expect(sizeProps).toBeDefined()
      const parsedSize = JSON.parse(sizeProps || '{}')
      expect(parsedSize).toEqual({ base: 'sm', md: 'md' })
    })

    it('should render table header', () => {
      render(<PendingItems />)
      const tableHeader = screen.getByTestId('table-header')
      expect(tableHeader).toBeInTheDocument()
    })

    it('should render table body', () => {
      render(<PendingItems />)
      const tableBody = screen.getByTestId('table-body')
      expect(tableBody).toBeInTheDocument()
    })
  })

  describe('Table Headers', () => {
    it('should render exactly 4 column headers', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders).toHaveLength(4)
    })

    it('should render ID column header', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[0]).toHaveTextContent('ID')
    })

    it('should render Title column header', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[1]).toHaveTextContent('Title')
    })

    it('should render Description column header', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[2]).toHaveTextContent('Description')
    })

    it('should render Actions column header', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[3]).toHaveTextContent('Actions')
    })

    it('should set column header width to sm', () => {
      render(<PendingItems />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      columnHeaders.forEach((header) => {
        expect(header.getAttribute('data-width')).toBe('sm')
      })
    })
  })

  describe('Table Body Rows', () => {
    it('should render exactly 5 rows in table body', () => {
      render(<PendingItems />)
      const tableRows = screen.getAllByTestId('table-row')
      // 1 header row + 5 body rows = 6 total
      expect(tableRows).toHaveLength(6)
    })

    it('should render 4 cells per body row', () => {
      render(<PendingItems />)
      const tableRows = screen.getAllByTestId('table-row')
      // Skip the first row which is the header
      const bodyRows = tableRows.slice(1)
      bodyRows.forEach((row) => {
        const cells = row.querySelectorAll('[data-testid="table-cell"]')
        expect(cells).toHaveLength(4)
      })
    })

    it('should render SkeletonText in each cell', () => {
      render(<PendingItems />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      // 5 rows * 4 cells = 20 skeleton texts
      expect(skeletonTexts).toHaveLength(20)
    })

    it('should pass noOfLines={1} to each SkeletonText', () => {
      render(<PendingItems />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      skeletonTexts.forEach((skeleton) => {
        expect(skeleton.getAttribute('data-nooflines')).toBe('1')
      })
    })
  })

  describe('Array Iteration', () => {
    it('should iterate exactly 5 times', () => {
      render(<PendingItems />)
      const tableCells = screen.getAllByTestId('table-cell')
      // 5 rows * 4 cells = 20 cells total
      expect(tableCells).toHaveLength(20)
    })

    it('should use index as key for map function', () => {
      const { container } = render(<PendingItems />)
      const tableRows = container.querySelectorAll('[data-testid="table-row"]')
      // Verify rows are rendered (keys are used internally by React)
      expect(tableRows.length).toBeGreaterThan(0)
    })
  })

  describe('Structure Integration', () => {
    it('should structure table correctly with header and body', () => {
      const { container } = render(<PendingItems />)
      const tableRoot = screen.getByTestId('table-root')
      const header = screen.getByTestId('table-header')
      const body = screen.getByTestId('table-body')

      expect(tableRoot).toContainElement(header)
      expect(tableRoot).toContainElement(body)
    })

    it('should render complete table structure', () => {
      render(<PendingItems />)

      // Verify all structural elements exist
      expect(screen.getByTestId('table-root')).toBeInTheDocument()
      expect(screen.getByTestId('table-header')).toBeInTheDocument()
      expect(screen.getByTestId('table-body')).toBeInTheDocument()

      // Verify row counts
      const bodyRows = screen.getAllByTestId('table-row').slice(1) // Exclude header row
      expect(bodyRows).toHaveLength(5)
    })

    it('should maintain consistent column structure across all rows', () => {
      render(<PendingItems />)
      const tableCells = screen.getAllByTestId('table-cell')

      // Every 4 cells should represent one row
      for (let i = 0; i < tableCells.length; i += 4) {
        expect(i + 3 < tableCells.length).toBe(true)
      }
    })
  })

  describe('Export', () => {
    it('should export PendingItems as default export', () => {
      expect(PendingItems).toBeDefined()
      expect(typeof PendingItems).toBe('function')
    })
  })

  describe('Edge Cases', () => {
    it('should handle multiple renders without errors', () => {
      const { rerender } = render(<PendingItems />)
      expect(() => {
        rerender(<PendingItems />)
      }).not.toThrow()
    })

    it('should render consistently on re-renders', () => {
      const { rerender } = render(<PendingItems />)
      let initialCells = screen.getAllByTestId('table-cell').length
      expect(initialCells).toBe(20)

      rerender(<PendingItems />)
      let afterRenderCells = screen.getAllByTestId('table-cell').length
      expect(afterRenderCells).toBe(20)
    })
  })

  describe('Empty Array Creation', () => {
    it('should correctly spread Array(5) into an array', () => {
      render(<PendingItems />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      // Verify exactly 5 iterations occurred (5 rows * 4 skeletons = 20)
      expect(skeletonTexts).toHaveLength(20)
    })
  })

  describe('Responsive Sizing', () => {
    it('should apply responsive size configuration', () => {
      render(<PendingItems />)
      const tableRoot = screen.getByTestId('table-root')
      const sizeData = tableRoot.getAttribute('data-size')
      expect(sizeData).toContain('sm')
      expect(sizeData).toContain('md')
    })
  })
})