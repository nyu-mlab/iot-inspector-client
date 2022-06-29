import React from 'react'
import Select from 'react-select'
import Label from './label'

const groupStyles = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}

const groupBadgeStyles = {
  backgroundColor: '#EBECF0',
  borderRadius: '2em',
  color: '#172B4D',
  display: 'inline-block',
  fontSize: 12,
  fontWeight: 'normal',
  lineHeight: '1',
  minWidth: 1,
  padding: '0.16666666666667em 0.5em',
  textAlign: 'center',
}

const formatGroupLabel = (data) => (
  <div style={groupStyles}>
    <span>{data.label}</span>
    <span style={groupBadgeStyles}>{data.options.length}</span>
  </div>
)

const SelectInput = (props) => {
  const {
    className,
    form:{ errors, submitCount },
    field,
    hint,
    placeholder,
    defaultValue,
    label,
    isMulti,
    isSearchable,
    type,
    onChange,
    options,
  } = props
  // const status = errors[field.name] ? 'is-invalid' : ''

  const getSingleSelectValue = () => {
    return field.value && options.find(o => o.value === field.value)
  }

  const getMultiSelectValues = () => {
    return field.value && field.value.map(value => options.find(o => o.value === value))
  }

  return (
    <div className={`form-group ${className}}`}>
      <Label label={label} hint={hint} />
      <div>
        <Select
          // NOTE: I've left field commented out, and inplace add value
          // Value is looking for the label and assigning it. This works so that
          // we can return a single value. For more info, see here:
          // https://github.com/JedWatson/react-select/issues/2974#issuecomment-416232139
          // {...field}
          value={isMulti ? getMultiSelectValues() : getSingleSelectValue()}
          type={type}
          options={options}
          defaultValue={defaultValue}
          formatGroupLabel={formatGroupLabel}
          onChange={onChange}
          placeholder={placeholder}
          isMulti={isMulti}
          isSearchable={isSearchable}
          isClearable
          className="react-select-container"
          classNamePrefix="react-select"
        />
        {submitCount > 0 && errors[field.name] && (
          <div className="text-danger">
            {errors[field.name]}</div>
        )}
      </div>
    </div>
  )
}

export default SelectInput
