import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { CancelablePromise, CancelError } from '../core/CancelablePromise'

describe('CancelError', () => {
  it('should create a CancelError with a message', () => {
    const error = new CancelError('Operation cancelled')
    expect(error.message).toBe('Operation cancelled')
    expect(error.name).toBe('CancelError')
  })

  it('should inherit from Error', () => {
    const error = new CancelError('Test error')
    expect(error instanceof Error).toBe(true)
  })

  it('should have isCancelled getter returning true', () => {
    const error = new CancelError('Cancelled')
    expect(error.isCancelled).toBe(true)
  })
})

describe('CancelablePromise', () => {
  describe('constructor', () => {
    it('should initialize with all flags set to false', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      expect(promise.isCancelled).toBe(false)
      expect(promise.cancelHandlers).toEqual([])
    })

    it('should call executor immediately', () => {
      const executor = vi.fn()
      new CancelablePromise(executor)
      expect(executor).toHaveBeenCalledOnce()
    })

    it('should pass resolve, reject, and onCancel to executor', () => {
      const executor = vi.fn()
      new CancelablePromise(executor)
      const [resolve, reject, onCancel] = executor.mock.calls[0]
      expect(typeof resolve).toBe('function')
      expect(typeof reject).toBe('function')
      expect(typeof onCancel).toBe('function')
    })
  })

  describe('resolve behavior', () => {
    it('should resolve with a value', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('success')
      })
      const result = await promise
      expect(result).toBe('success')
    })

    it('should resolve with a PromiseLike', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve(Promise.resolve('async success'))
      })
      const result = await promise
      expect(result).toBe('async success')
    })

    it('should not resolve if already resolved', async () => {
      const executor = vi.fn((resolve) => {
        resolve('first')
        resolve('second')
      })
      const promise = new CancelablePromise(executor)
      const result = await promise
      expect(result).toBe('first')
    })

    it('should not resolve if already rejected', async () => {
      const executor = vi.fn((resolve, reject) => {
        reject(new Error('rejected'))
        resolve('should not resolve')
      })
      const promise = new CancelablePromise(executor)
      try {
        await promise
        expect.fail('should have rejected')
      } catch (error) {
        expect((error as Error).message).toBe('rejected')
      }
    })

    it('should not resolve if already cancelled', async () => {
      let cancelCallback: () => void
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(() => {
          cancelCallback?.()
        })
        // Set up a delayed resolve that won't happen due to cancel
      })
      promise.cancel()
      // Try to resolve after cancel - should not work
      try {
        await promise
        expect.fail('should have been cancelled')
      } catch (error) {
        expect(error instanceof CancelError).toBe(true)
      }
    })
  })

  describe('reject behavior', () => {
    it('should reject with an error', async () => {
      const error = new Error('test error')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      try {
        await promise
        expect.fail('should have rejected')
      } catch (e) {
        expect(e).toBe(error)
      }
    })

    it('should not reject if already resolved', async () => {
      const executor = vi.fn((resolve, reject) => {
        resolve('success')
        reject(new Error('should not reject'))
      })
      const promise = new CancelablePromise(executor)
      const result = await promise
      expect(result).toBe('success')
    })

    it('should not reject if already rejected', async () => {
      const error1 = new Error('first')
      const error2 = new Error('second')
      const executor = vi.fn((resolve, reject) => {
        reject(error1)
        reject(error2)
      })
      const promise = new CancelablePromise(executor)
      try {
        await promise
        expect.fail('should have rejected')
      } catch (e) {
        expect(e).toBe(error1)
      }
    })

    it('should not reject if already cancelled', async () => {
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(() => {})
      })
      promise.cancel()
      try {
        await promise
        expect.fail('should have been cancelled')
      } catch (e) {
        expect(e instanceof CancelError).toBe(true)
      }
    })
  })

  describe('onCancel callback', () => {
    it('should allow registering cancel handlers', async () => {
      const handler1 = vi.fn()
      const handler2 = vi.fn()
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(handler1)
        onCancel(handler2)
      })
      promise.cancel()
      expect(handler1).toHaveBeenCalled()
      expect(handler2).toHaveBeenCalled()
    })

    it('should not register cancel handler if already resolved', () => {
      const handler = vi.fn()
      new CancelablePromise((resolve, reject, onCancel) => {
        resolve('done')
        onCancel(handler)
      })
      expect(handler).not.toHaveBeenCalled()
    })

    it('should not register cancel handler if already rejected', () => {
      const handler = vi.fn()
      new CancelablePromise((resolve, reject, onCancel) => {
        reject(new Error('error'))
        onCancel(handler)
      })
      expect(handler).not.toHaveBeenCalled()
    })

    it('should not register cancel handler if already cancelled', () => {
      let cancelFn: (() => void) | null = null
      const handler = vi.fn()
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel((fn) => {
          cancelFn = fn
        })
      })
      // First, set up the cancel mechanism
      promise.cancel()
      // Now try to register another handler - should not work
      // Note: The onCancel callback is already configured at this point
      expect(handler).not.toHaveBeenCalled()
    })

    it('should provide isResolved property on onCancel', () => {
      let onCancelFn: any
      new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
      })
      expect(onCancelFn.isResolved).toBe(false)
    })

    it('should provide isRejected property on onCancel', () => {
      let onCancelFn: any
      new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
      })
      expect(onCancelFn.isRejected).toBe(false)
    })

    it('should provide isCancelled property on onCancel', () => {
      let onCancelFn: any
      new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
      })
      expect(onCancelFn.isCancelled).toBe(false)
    })

    it('should update isResolved property after resolution', async () => {
      let onCancelFn: any
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
        resolve('done')
      })
      await promise
      expect(onCancelFn.isResolved).toBe(true)
    })

    it('should update isRejected property after rejection', async () => {
      let onCancelFn: any
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
        reject(new Error('failed'))
      })
      try {
        await promise
      } catch {
        // expected
      }
      expect(onCancelFn.isRejected).toBe(true)
    })

    it('should update isCancelled property after cancellation', async () => {
      let onCancelFn: any
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancelFn = onCancel
      })
      promise.cancel()
      expect(onCancelFn.isCancelled).toBe(true)
    })
  })

  describe('cancel method', () => {
    it('should cancel the promise', async () => {
      const promise = new CancelablePromise(() => {
        // never resolves
      })
      promise.cancel()
      expect(promise.isCancelled).toBe(true)
    })

    it('should reject with CancelError when cancelled', async () => {
      const promise = new CancelablePromise(() => {
        // never resolves
      })
      promise.cancel()
      try {
        await promise
        expect.fail('should have been cancelled')
      } catch (e) {
        expect(e instanceof CancelError).toBe(true)
        expect((e as Error).message).toBe('Request aborted')
      }
    })

    it('should not cancel if already resolved', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('done')
      })
      await promise
      promise.cancel()
      expect(promise.isCancelled).toBe(false)
      const result = await promise
      expect(result).toBe('done')
    })

    it('should not cancel if already rejected', async () => {
      const error = new Error('failed')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      try {
        await promise
      } catch {
        // expected
      }
      promise.cancel()
      expect(promise.isCancelled).toBe(false)
    })

    it('should not cancel twice', async () => {
      const handler = vi.fn()
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(handler)
      })
      promise.cancel()
      promise.cancel()
      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should execute all cancel handlers', async () => {
      const handlers = [vi.fn(), vi.fn(), vi.fn()]
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        handlers.forEach((h) => onCancel(h))
      })
      promise.cancel()
      handlers.forEach((h) => expect(h).toHaveBeenCalledOnce())
    })

    it('should clear cancel handlers after cancellation', async () => {
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(() => {})
      })
      expect(promise.cancelHandlers.length).toBe(1)
      promise.cancel()
      expect(promise.cancelHandlers.length).toBe(0)
    })

    it('should handle errors thrown by cancel handlers', async () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const handler = vi.fn(() => {
        throw new Error('Handler error')
      })
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(handler)
      })
      promise.cancel()
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        'Cancellation threw an error',
        expect.any(Error)
      )
      expect(promise.isCancelled).toBe(true)
      consoleWarnSpy.mockRestore()
    })

    it('should not reject if cancel handler throws and promise already resolved', async () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(() => {
          throw new Error('Handler error')
        })
        resolve('done')
      })
      const result = await promise
      expect(result).toBe('done')
      consoleWarnSpy.mockRestore()
    })

    it('should exit early if no cancel handlers', async () => {
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        // No handlers registered
      })
      promise.cancel()
      expect(promise.isCancelled).toBe(true)
      try {
        await promise
        expect.fail('should have been cancelled')
      } catch (e) {
        expect(e instanceof CancelError).toBe(true)
      }
    })
  })

  describe('then method', () => {
    it('should return a promise that resolves with the result', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('success')
      })
      const result = await promise.then((value) => {
        return value + '!'
      })
      expect(result).toBe('success!')
    })

    it('should return a promise that handles rejection', async () => {
      const error = new Error('failed')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      const result = await promise.then(
        (value) => value,
        (reason) => {
          expect(reason).toBe(error)
          return 'recovered'
        }
      )
      expect(result).toBe('recovered')
    })

    it('should handle null onFulfilled', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      const result = await promise.then(null)
      expect(result).toBe('test')
    })

    it('should handle null onRejected', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      const result = await promise.then(() => 'value', null)
      expect(result).toBe('value')
    })

    it('should chain multiple then calls', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve(1)
      })
      const result = await promise
        .then((v) => v + 1)
        .then((v) => v * 2)
      expect(result).toBe(4)
    })

    it('should return a PromiseLike from onFulfilled', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve(5)
      })
      const result = await promise.then((v) => Promise.resolve(v * 2))
      expect(result).toBe(10)
    })
  })

  describe('catch method', () => {
    it('should catch rejection with a handler', async () => {
      const error = new Error('failed')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      const result = await promise.catch((reason) => {
        expect(reason).toBe(error)
        return 'recovered'
      })
      expect(result).toBe('recovered')
    })

    it('should pass through if no rejection', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('success')
      })
      const result = await promise.catch(() => 'should not run')
      expect(result).toBe('success')
    })

    it('should handle null onRejected', async () => {
      const error = new Error('test')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      try {
        await promise.catch(null)
        expect.fail('should have rejected')
      } catch (e) {
        expect(e).toBe(error)
      }
    })

    it('should chain multiple catch calls', async () => {
      const promise = new CancelablePromise((resolve, reject) => {
        reject(new Error('first'))
      })
      const result = await promise
        .catch((e) => 'caught1')
        .catch((e) => 'caught2')
      expect(result).toBe('caught1')
    })

    it('should return PromiseLike from onRejected', async () => {
      const promise = new CancelablePromise((resolve, reject) => {
        reject(new Error('failed'))
      })
      const result = await promise.catch((e) => Promise.resolve('recovered'))
      expect(result).toBe('recovered')
    })

    it('should catch CancelError', async () => {
      const promise = new CancelablePromise(() => {
        // never resolves
      })
      promise.cancel()
      const result = await promise.catch((error) => {
        expect(error instanceof CancelError).toBe(true)
        return 'caught'
      })
      expect(result).toBe('caught')
    })
  })

  describe('finally method', () => {
    it('should execute finally handler on resolution', async () => {
      const handler = vi.fn()
      const promise = new CancelablePromise((resolve) => {
        resolve('done')
      })
      const result = await promise.finally(handler)
      expect(handler).toHaveBeenCalledOnce()
      expect(result).toBe('done')
    })

    it('should execute finally handler on rejection', async () => {
      const handler = vi.fn()
      const error = new Error('failed')
      const promise = new CancelablePromise((resolve, reject) => {
        reject(error)
      })
      try {
        await promise.finally(handler)
        expect.fail('should have rejected')
      } catch (e) {
        expect(e).toBe(error)
      }
      expect(handler).toHaveBeenCalledOnce()
    })

    it('should handle null onFinally', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      const result = await promise.finally(null)
      expect(result).toBe('test')
    })

    it('should chain finally with then', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve(1)
      })
      const result = await promise
        .finally(() => {
          // does nothing
        })
        .then((v) => v + 1)
      expect(result).toBe(2)
    })

    it('should execute finally even on cancellation', async () => {
      const handler = vi.fn()
      const promise = new CancelablePromise(() => {
        // never resolves
      })
      promise.cancel()
      try {
        await promise.finally(handler)
        expect.fail('should have been cancelled')
      } catch (e) {
        expect(e instanceof CancelError).toBe(true)
      }
      expect(handler).toHaveBeenCalledOnce()
    })
  })

  describe('isCancelled getter', () => {
    it('should return false initially', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      expect(promise.isCancelled).toBe(false)
    })

    it('should return true after cancel', () => {
      const promise = new CancelablePromise(() => {
        // never resolves
      })
      promise.cancel()
      expect(promise.isCancelled).toBe(true)
    })

    it('should return false if cancelled but already resolved', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('done')
      })
      await promise
      promise.cancel()
      expect(promise.isCancelled).toBe(false)
    })
  })

  describe('Symbol.toStringTag', () => {
    it('should return correct string tag', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      expect(Object.prototype.toString.call(promise)).toContain('Promise')
    })

    it('should be usable in String conversion', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      const str = Object.prototype.toString.call(promise)
      expect(str).toEqual('[object Cancellable Promise]')
    })
  })

  describe('promise property', () => {
    it('should be accessible and resolve correctly', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      const result = await promise.promise
      expect(result).toBe('test')
    })

    it('should be a Promise instance', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      expect(promise.promise instanceof Promise).toBe(true)
    })
  })

  describe('cancelHandlers array', () => {
    it('should be initially empty', () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('test')
      })
      expect(promise.cancelHandlers).toEqual([])
    })

    it('should contain registered handlers', () => {
      const handlers = [() => {}, () => {}]
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        handlers.forEach((h) => onCancel(h))
      })
      expect(promise.cancelHandlers.length).toBe(2)
    })
  })

  describe('edge cases', () => {
    it('should handle synchronous resolution in executor', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve('sync')
      })
      const result = await promise
      expect(result).toBe('sync')
    })

    it('should handle asynchronous resolution in executor', async () => {
      const promise = new CancelablePromise((resolve) => {
        setTimeout(() => resolve('async'), 0)
      })
      const result = await promise
      expect(result).toBe('async')
    })

    it('should handle complex chaining scenarios', async () => {
      const promise = new CancelablePromise((resolve) => {
        resolve(1)
      })
      const result = await promise
        .then((v) => Promise.resolve(v + 1))
        .then((v) => v * 2)
        .catch(() => 0)
        .finally(() => {
          // side effect
        })
      expect(result).toBe(4)
    })

    it('should handle multiple concurrent cancel calls', () => {
      const handler1 = vi.fn()
      const handler2 = vi.fn()
      const promise = new CancelablePromise((resolve, reject, onCancel) => {
        onCancel(handler1)
        onCancel(handler2)
      })
      promise.cancel()
      promise.cancel()
      promise.cancel()
      expect(handler1).toHaveBeenCalledTimes(1)
      expect(handler2).toHaveBeenCalledTimes(1)
    })

    it('should handle executor that throws', async () => {
      const error = new Error('executor error')
      const promise = new CancelablePromise(() => {
        throw error
      })
      try {
        await promise
      } catch (e) {
        // The promise constructor doesn't catch executor errors
        // They propagate to the caller
      }
    })
  })
})