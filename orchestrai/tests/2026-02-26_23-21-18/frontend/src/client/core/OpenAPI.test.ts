import { describe, it, expect, beforeEach } from "vitest"
import { Interceptors, OpenAPI } from "./OpenAPI"
import type { AxiosRequestConfig, AxiosResponse } from "axios"

describe("Interceptors", () => {
  let interceptors: Interceptors<AxiosRequestConfig>

  beforeEach(() => {
    interceptors = new Interceptors()
  })

  describe("constructor", () => {
    it("should initialize with empty _fns array", () => {
      expect(interceptors._fns).toEqual([])
    })
  })

  describe("use", () => {
    it("should add middleware function to _fns array", () => {
      const fn = (value: AxiosRequestConfig) => value
      interceptors.use(fn)
      expect(interceptors._fns).toContain(fn)
      expect(interceptors._fns.length).toBe(1)
    })

    it("should add multiple middleware functions", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      expect(interceptors._fns).toEqual([fn1, fn2])
    })

    it("should preserve order of middleware functions", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      const fn3 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      interceptors.use(fn3)
      expect(interceptors._fns[0]).toBe(fn1)
      expect(interceptors._fns[1]).toBe(fn2)
      expect(interceptors._fns[2]).toBe(fn3)
    })
  })

  describe("eject", () => {
    it("should remove middleware function from _fns array", () => {
      const fn = (value: AxiosRequestConfig) => value
      interceptors.use(fn)
      expect(interceptors._fns).toContain(fn)
      interceptors.eject(fn)
      expect(interceptors._fns).not.toContain(fn)
      expect(interceptors._fns.length).toBe(0)
    })

    it("should not modify array if function not found", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      const originalLength = interceptors._fns.length
      interceptors.eject(fn2)
      expect(interceptors._fns.length).toBe(originalLength)
      expect(interceptors._fns).toContain(fn1)
    })

    it("should remove function from middle of array", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      const fn3 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      interceptors.use(fn3)
      interceptors.eject(fn2)
      expect(interceptors._fns).toEqual([fn1, fn3])
    })

    it("should remove function from start of array", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      const fn3 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      interceptors.use(fn3)
      interceptors.eject(fn1)
      expect(interceptors._fns).toEqual([fn2, fn3])
    })

    it("should remove function from end of array", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      const fn3 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      interceptors.use(fn3)
      interceptors.eject(fn3)
      expect(interceptors._fns).toEqual([fn1, fn2])
    })

    it("should create new array reference when ejecting", () => {
      const fn1 = (value: AxiosRequestConfig) => value
      const fn2 = (value: AxiosRequestConfig) => value
      interceptors.use(fn1)
      interceptors.use(fn2)
      const originalArray = interceptors._fns
      interceptors.eject(fn1)
      expect(interceptors._fns).not.toBe(originalArray)
    })

    it("should handle eject from single-element array", () => {
      const fn = (value: AxiosRequestConfig) => value
      interceptors.use(fn)
      interceptors.eject(fn)
      expect(interceptors._fns).toEqual([])
    })
  })
})

describe("OpenAPI config object", () => {
  it("should have BASE as empty string", () => {
    expect(OpenAPI.BASE).toBe("")
  })

  it("should have CREDENTIALS set to 'include'", () => {
    expect(OpenAPI.CREDENTIALS).toBe("include")
  })

  it("should have ENCODE_PATH as undefined", () => {
    expect(OpenAPI.ENCODE_PATH).toBeUndefined()
  })

  it("should have HEADERS as undefined", () => {
    expect(OpenAPI.HEADERS).toBeUndefined()
  })

  it("should have PASSWORD as undefined", () => {
    expect(OpenAPI.PASSWORD).toBeUndefined()
  })

  it("should have TOKEN as undefined", () => {
    expect(OpenAPI.TOKEN).toBeUndefined()
  })

  it("should have USERNAME as undefined", () => {
    expect(OpenAPI.USERNAME).toBeUndefined()
  })

  it("should have VERSION set to '0.1.0'", () => {
    expect(OpenAPI.VERSION).toBe("0.1.0")
  })

  it("should have WITH_CREDENTIALS as false", () => {
    expect(OpenAPI.WITH_CREDENTIALS).toBe(false)
  })

  it("should have interceptors.request as Interceptors instance", () => {
    expect(OpenAPI.interceptors.request).toBeInstanceOf(Interceptors)
  })

  it("should have interceptors.response as Interceptors instance", () => {
    expect(OpenAPI.interceptors.response).toBeInstanceOf(Interceptors)
  })

  it("should have separate interceptors for request and response", () => {
    expect(OpenAPI.interceptors.request).not.toBe(
      OpenAPI.interceptors.response,
    )
  })
})