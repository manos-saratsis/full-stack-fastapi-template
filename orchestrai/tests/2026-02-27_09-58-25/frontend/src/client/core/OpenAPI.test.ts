import { describe, it, expect, beforeEach } from 'vitest'
import { Interceptors, OpenAPI } from './OpenAPI'
import type { AxiosRequestConfig, AxiosResponse } from 'axios'

describe('Interceptors', () => {
  let interceptors: Interceptors<AxiosRequestConfig>

  beforeEach(() => {
    interceptors = new Interceptors()
  })

  describe('constructor', () => {
    it('should initialize with empty functions array', () => {
      expect(interceptors._fns).toEqual([])
    })
  })

  describe('use', () => {
    it('should add a middleware function to the array', () => {
      const middleware = (value: AxiosRequestConfig) => value
      interceptors.use(middleware)
      expect(interceptors._fns).toContain(middleware)
      expect(interceptors._fns.length).toBe(1)
    })

    it('should add multiple middleware functions in order', () => {
      const middleware1 = (value: AxiosRequestConfig) => value
      const middleware2 = (value: AxiosRequestConfig) => value
      interceptors.use(middleware1)
      interceptors.use(middleware2)
      expect(interceptors._fns).toEqual([middleware1, middleware2])
      expect(interceptors._fns.length).toBe(2)
    })

    it('should create a new array reference when adding middleware', () => {
      const originalArray = interceptors._fns
      const middleware = (value: AxiosRequestConfig) => value
      interceptors.use(middleware)
      expect(interceptors._fns).not.toBe(originalArray)
    })
  })

  describe('eject', () => {
    it('should remove an existing middleware function', () => {
      const middleware = (value: AxiosRequestConfig) => value
      interceptors.use(middleware)
      expect(interceptors._fns.length).toBe(1)
      interceptors.eject(middleware)
      expect(interceptors._fns.length).toBe(0)
    })

    it('should not throw when ejecting a non-existent middleware', () => {
      const middleware1 = (value: AxiosRequestConfig) => value
      const middleware2 = (value: AxiosRequestConfig) => value
      interceptors.use(middleware1)
      expect(() => {
        interceptors.eject(middleware2)
      }).not.toThrow()
      expect(interceptors._fns.length).toBe(1)
    })

    it('should remove middleware from the middle of the array', () => {
      const middleware1 = (value: AxiosRequestConfig) => value
      const middleware2 = (value: AxiosRequestConfig) => value
      const middleware3 = (value: AxiosRequestConfig) => value
      interceptors.use(middleware1)
      interceptors.use(middleware2)
      interceptors.use(middleware3)
      interceptors.eject(middleware2)
      expect(interceptors._fns).toEqual([middleware1, middleware3])
    })

    it('should remove only the first instance of a middleware', () => {
      const middleware = (value: AxiosRequestConfig) => value
      interceptors.use(middleware)
      interceptors.use(middleware)
      interceptors.eject(middleware)
      expect(interceptors._fns.length).toBe(1)
      expect(interceptors._fns[0]).toBe(middleware)
    })

    it('should create a new array reference when ejecting middleware', () => {
      const middleware = (value: AxiosRequestConfig) => value
      interceptors.use(middleware)
      const originalArray = interceptors._fns
      interceptors.eject(middleware)
      expect(interceptors._fns).not.toBe(originalArray)
    })
  })

  describe('eject with response interceptors', () => {
    it('should work with AxiosResponse interceptors', () => {
      const responseInterceptors = new Interceptors<AxiosResponse>()
      const middleware = (value: AxiosResponse) => value
      responseInterceptors.use(middleware)
      responseInterceptors.eject(middleware)
      expect(responseInterceptors._fns.length).toBe(0)
    })
  })
})

describe('OpenAPI config object', () => {
  it('should have correct default BASE value', () => {
    expect(OpenAPI.BASE).toBe('')
  })

  it('should have correct default CREDENTIALS value', () => {
    expect(OpenAPI.CREDENTIALS).toBe('include')
  })

  it('should have undefined ENCODE_PATH by default', () => {
    expect(OpenAPI.ENCODE_PATH).toBeUndefined()
  })

  it('should have undefined HEADERS by default', () => {
    expect(OpenAPI.HEADERS).toBeUndefined()
  })

  it('should have undefined PASSWORD by default', () => {
    expect(OpenAPI.PASSWORD).toBeUndefined()
  })

  it('should have undefined TOKEN by default', () => {
    expect(OpenAPI.TOKEN).toBeUndefined()
  })

  it('should have undefined USERNAME by default', () => {
    expect(OpenAPI.USERNAME).toBeUndefined()
  })

  it('should have correct default VERSION', () => {
    expect(OpenAPI.VERSION).toBe('0.1.0')
  })

  it('should have correct default WITH_CREDENTIALS', () => {
    expect(OpenAPI.WITH_CREDENTIALS).toBe(false)
  })

  it('should have interceptors object with request and response', () => {
    expect(OpenAPI.interceptors).toBeDefined()
    expect(OpenAPI.interceptors.request).toBeDefined()
    expect(OpenAPI.interceptors.response).toBeDefined()
  })

  it('should have request interceptor as Interceptors instance', () => {
    expect(OpenAPI.interceptors.request).toBeInstanceOf(Interceptors)
  })

  it('should have response interceptor as Interceptors instance', () => {
    expect(OpenAPI.interceptors.response).toBeInstanceOf(Interceptors)
  })

  it('should allow modification of BASE', () => {
    const originalBase = OpenAPI.BASE
    OpenAPI.BASE = 'https://api.example.com'
    expect(OpenAPI.BASE).toBe('https://api.example.com')
    OpenAPI.BASE = originalBase
  })

  it('should allow modification of TOKEN', () => {
    const originalToken = OpenAPI.TOKEN
    OpenAPI.TOKEN = 'test-token'
    expect(OpenAPI.TOKEN).toBe('test-token')
    OpenAPI.TOKEN = originalToken
  })

  it('should allow modification of other properties', () => {
    const originalWithCredentials = OpenAPI.WITH_CREDENTIALS
    OpenAPI.WITH_CREDENTIALS = true
    expect(OpenAPI.WITH_CREDENTIALS).toBe(true)
    OpenAPI.WITH_CREDENTIALS = originalWithCredentials
  })
})