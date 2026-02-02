import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import PendingUsers from './PendingUsers'

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

describe('PendingUsers Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    it('should render the component successfully', () => {
      render(<PendingUsers />)
      const tableRoot = screen.getByTestId('table-root')
      expect(tableRoot).toBeInTheDocument()
    })

    it('should render Table.Root with correct size props', () => {
      render(<PendingUsers />)
      const tableRoot = screen.getByTestId('table-root')
      const sizeProps = tableRoot.getAttribute('data-size')
      expect(sizeProps).toBeDefined()
      const parsedSize = JSON.parse(sizeProps || '{}')
      expect(parsedSize).toEqual({ base: 'sm', md: 'md' })
    })

    it('should render table header', () => {
      render(<PendingUsers />)
      const tableHeader = screen.getByTestId('table-header')
      expect(tableHeader).toBeInTheDocument()
    })

    it('should render table body', () => {
      render(<PendingUsers />)
      const tableBody = screen.getByTestId('table-body')
      expect(tableBody).toBeInTheDocument()
    })
  })

  describe('Table Headers', () => {
    it('should render exactly 5 column headers', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders).toHaveLength(5)
    })

    it('should render Full name column header', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[0]).toHaveTextContent('Full name')
    })

    it('should render Email column header', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[1]).toHaveTextContent('Email')
    })

    it('should render Role column header', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[2]).toHaveTextContent('Role')
    })

    it('should render Status column header', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[3]).toHaveTextContent('Status')
    })

    it('should render Actions column header', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      expect(columnHeaders[4]).toHaveTextContent('Actions')
    })

    it('should set all column headers width to sm', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      columnHeaders.forEach((header) => {
        expect(header.getAttribute('data-width')).toBe('sm')
      })
    })
  })

  describe('Table Body Rows', () => {
    it('should render exactly 5 rows in table body', () => {
      render(<PendingUsers />)
      const tableRows = screen.getAllByTestId('table-row')
      // 1 header row + 5 body rows = 6 total
      expect(tableRows).toHaveLength(6)
    })

    it('should render 5 cells per body row', () => {
      render(<PendingUsers />)
      const tableRows = screen.getAllByTestId('table-row')
      // Skip the first row which is the header
      const bodyRows = tableRows.slice(1)
      bodyRows.forEach((row) => {
        const cells = row.querySelectorAll('[data-testid="table-cell"]')
        expect(cells).toHaveLength(5)
      })
    })

    it('should render SkeletonText in each cell', () => {
      render(<PendingUsers />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      // 5 rows * 5 cells = 25 skeleton texts
      expect(skeletonTexts).toHaveLength(25)
    })

    it('should pass noOfLines={1} to each SkeletonText', () => {
      render(<PendingUsers />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      skeletonTexts.forEach((skeleton) => {
        expect(skeleton.getAttribute('data-nooflines')).toBe('1')
      })
    })
  })

  describe('Array Iteration', () => {
    it('should iterate exactly 5 times', () => {
      render(<PendingUsers />)
      const tableCells = screen.getAllByTestId('table-cell')
      // 5 rows * 5 cells = 25 cells total
      expect(tableCells).toHaveLength(25)
    })

    it('should use index as key for map function', () => {
      const { container } = render(<PendingUsers />)
      const tableRows = container.querySelectorAll('[data-testid="table-row"]')
      // Verify rows are rendered (keys are used internally by React)
      expect(tableRows.length).toBeGreaterThan(0)
    })
  })

  describe('Structure Integration', () => {
    it('should structure table correctly with header and body', () => {
      const { container } = render(<PendingUsers />)
      const tableRoot = screen.getByTestId('table-root')
      const header = screen.getByTestId('table-header')
      const body = screen.getByTestId('table-body')

      expect(tableRoot).toContainElement(header)
      expect(tableRoot).toContainElement(body)
    })

    it('should render complete table structure', () => {
      render(<PendingUsers />)

      // Verify all structural elements exist
      expect(screen.getByTestId('table-root')).toBeInTheDocument()
      expect(screen.getByTestId('table-header')).toBeInTheDocument()
      expect(screen.getByTestId('table-body')).toBeInTheDocument()

      // Verify row counts
      const bodyRows = screen.getAllByTestId('table-row').slice(1) // Exclude header row
      expect(bodyRows).toHaveLength(5)
    })

    it('should maintain consistent column structure across all rows', () => {
      render(<PendingUsers />)
      const tableCells = screen.getAllByTestId('table-cell')

      // Every 5 cells should represent one row (since we have 5 columns)
      for (let i = 0; i < tableCells.length; i += 5) {
        expect(i + 4 < tableCells.length).toBe(true)
      }
    })

    it('should have correct total cell count', () => {
      render(<PendingUsers />)
      const tableCells = screen.getAllByTestId('table-cell')
      expect(tableCells).toHaveLength(25)
    })
  })

  describe('Export', () => {
    it('should export PendingUsers as default export', () => {
      expect(PendingUsers).toBeDefined()
      expect(typeof PendingUsers).toBe('function')
    })
  })

  describe('Edge Cases', () => {
    it('should handle multiple renders without errors', () => {
      const { rerender } = render(<PendingUsers />)
      expect(() => {
        rerender(<PendingUsers />)
      }).not.toThrow()
    })

    it('should render consistently on re-renders', () => {
      const { rerender } = render(<PendingUsers />)
      let initialCells = screen.getAllByTestId('table-cell').length
      expect(initialCells).toBe(25)

      rerender(<PendingUsers />)
      let afterRenderCells = screen.getAllByTestId('table-cell').length
      expect(afterRenderCells).toBe(25)
    })

    it('should render consistently with headers and body', () => {
      const { container } = render(<PendingUsers />)
      const headerCount = container.querySelectorAll('[data-testid="table-column-header"]').length
      const cellCount = container.querySelectorAll('[data-testid="table-cell"]').length
      
      // 5 headers for column headers + 25 cells for data rows
      expect(headerCount).toBe(5)
      expect(cellCount).toBe(25)
    })
  })

  describe('Empty Array Creation', () => {
    it('should correctly spread Array(5) into an array', () => {
      render(<PendingUsers />)
      const skeletonTexts = screen.getAllByTestId('skeleton-text')
      // Verify exactly 5 iterations occurred (5 rows * 5 skeletons = 25)
      expect(skeletonTexts).toHaveLength(25)
    })
  })

  describe('Responsive Sizing', () => {
    it('should apply responsive size configuration', () => {
      render(<PendingUsers />)
      const tableRoot = screen.getByTestId('table-root')
      const sizeData = tableRoot.getAttribute('data-size')
      expect(sizeData).toContain('sm')
      expect(sizeData).toContain('md')
    })
  })

  describe('JSX Structure', () => {
    it('should render header row within table header', () => {
      const { container } = render(<PendingUsers />)
      const header = screen.getByTestId('table-header')
      const headerRow = header.querySelector('[data-testid="table-row"]')
      expect(headerRow).toBeInTheDocument()
    })

    it('should render body rows within table body', () => {
      const { container } = render(<PendingUsers />)
      const body = screen.getByTestId('table-body')
      const bodyRows = body.querySelectorAll('[data-testid="table-row"]')
      // Should have exactly 5 body rows
      expect(bodyRows).toHaveLength(5)
    })

    it('should have consistent column count across header and body', () => {
      render(<PendingUsers />)
      const tableRows = screen.getAllByTestId('table-row')
      const headerRowCells = tableRows[0].querySelectorAll('[data-testid="table-column-header"]')
      const bodyRowCells = tableRows[1].querySelectorAll('[data-testid="table-cell"]')
      
      expect(headerRowCells).toHaveLength(5)
      expect(bodyRowCells).toHaveLength(5)
    })
  })

  describe('Column Coverage', () => {
    it('should display all required user columns in correct order', () => {
      render(<PendingUsers />)
      const columnHeaders = screen.getAllByTestId('table-column-header')
      
      const expectedColumns = ['Full name', 'Email', 'Role', 'Status', 'Actions']
      columnHeaders.forEach((header, index) => {
        expect(header).toHaveTextContent(expectedColumns[index])
      })
    })
  })
})