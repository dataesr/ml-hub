import { TextInput } from "@dataesr/dsfr-plus"
import React, { useState, useEffect, useRef } from "react"

interface SmartInputProps<T> {
  value: T
  onChange: (value: T) => void
  onError?: (nerror: string | null) => void
  validateSync?: (value: T) => string | null // Instant validation
  validateAsync?: (value: T) => Promise<string | null> // API validation
  debounceTime?: number
}
interface ComponentProps {
  component: React.ComponentType<any>
}
export const SmartInput = <T extends string | boolean | number>({
  component: Component,
  value,
  onChange,
  onError,
  validateSync,
  validateAsync,
  debounceTime = 1500,
  ...childProps
}: ComponentProps & SmartInputProps<T> & React.ComponentProps<typeof Component>) => {
  const [internalError, setInternalError] = useState<string | null>(null)
  const debounceTimer = useRef(null)

  const handleChange = (eventOrValue: any) => {
    const newValue = eventOrValue?.target ? eventOrValue.target.value : eventOrValue

    onChange(newValue)
    setInternalError(null)

    // Sync validation
    if (validateSync) {
      const errorMsg = validateSync(newValue)
      if (errorMsg) {
        setInternalError(errorMsg)
        onError(errorMsg)
        return
      } else {
        onError(null)
      }
    }

    // Async Validation (Debounced)
    if (validateAsync) {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)

      debounceTimer.current = setTimeout(async () => {
        try {
          const errorMsg = await validateAsync(newValue)
          setInternalError(errorMsg)
          onError(errorMsg)
        } catch (err) {
          console.error("Validation error", err)
        }
      }, debounceTime)
    }
  }

  useEffect(() => {
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
    }
  }, [])

  return (
    <Component
      {...childProps}
      value={value}
      onChange={handleChange}
      onSelectionChange={childProps.onSelectionChange ? handleChange : undefined}
      message={internalError || undefined}
      messageType={internalError ? "error" : undefined}
    />
  )
}

export function SmartTextInput({
  value,
  onChange,
  ...props
}: SmartInputProps<string> & React.ComponentProps<typeof TextInput>) {
  return <SmartInput {...props} value={value} onChange={onChange} component={TextInput} />
}
