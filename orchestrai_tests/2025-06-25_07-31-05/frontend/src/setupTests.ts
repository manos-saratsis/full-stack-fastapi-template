```typescript
import '@testing-library/jest-dom';
import 'jest-fetch-mock';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Reset all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});
```

These test files provide a solid foundation for testing the core functionality of the frontend application. They cover:

1. Authentication provider and context
2. Authentication service with API calls
3. Protected route component
4. Basic setup for Jest with TypeScript

To achieve 100% coverage, you would need to:

1. Add more test cases for edge cases
2. Test error boundaries
3. Add tests for all components
4. Test utilities and helpers
5. Test API integration points

Would you like me to generate additional test files for specific components or services?