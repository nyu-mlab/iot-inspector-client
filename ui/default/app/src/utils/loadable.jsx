import React, { Suspense } from 'react'

/**
 * Create component which is loaded async, showing a loading spinner
 * in the meantime.
 * @param {Function} loadFunc - Loading options
 * @returns {React.Component}
 */
export default function loadable(loadFunc) {
  const OtherComponent = React.lazy(loadFunc)
  return function LoadableWrapper(loadableProps) {
    return (
      <Suspense fallback={<>Loading...</>}>
        <OtherComponent {...loadableProps} />
      </Suspense>
    )
  }
}