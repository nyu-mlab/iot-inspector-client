import React, { useState } from 'react'
import Label from './label'

const TextInput = (props) => {
  const { children, className, hint, type, label, placeholder, autocomplete, onChange, required, field, form: { errors, touched }} = props
  const status = touched[field.name] && errors[field.name] ? 'is-invalid' : ''

  const [editing, setEditing] = useState(false)

  return (
    <>
      {children && !editing ? (
        <div className="editable" onClick={() => setEditing(true)}>
          {children}
        </div>
      ) : (
        <div className={`form-group ${className}`}>
            <Label label={label} hint={hint} />
          <input
            className={`form-control ${status}`}
            {...field}
            onChange={onChange}
            placeholder={placeholder}
            type={type}
            autoComplete={autocomplete}
            required={required}
          />
          {touched[field.name] && errors[field.name] && (
            <div className="invalid-feedback">{errors[field.name]}</div>
          )}
        </div>
      )}
    </>
  )
}

export default TextInput
