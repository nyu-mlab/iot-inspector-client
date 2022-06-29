import React from 'react'
import CreatableSelect from 'react-select/creatable'
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

const CreateSelect = ({
  className,
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
}) => {
  return (
    <div className={`form-group ${className}`}>
      <Label label={label} hint={hint} />
      <div>
        <CreatableSelect
          {...field}
          type={type}
          defaultValue={defaultValue}
          formatGroupLabel={formatGroupLabel}
          onChange={onChange}
          placeholder={placeholder}
          options={options}
          isMulti={isMulti}
          isSearchable={isSearchable}
          isClearable
          className="react-select-container"
          classNamePrefix="react-select"
          theme={(theme) => ({
            ...theme,
            borderRadius: 0,
            colors: {
              ...theme.colors,
              primary25: '#EBECF0',
              primary: '#172B4D',
            },
          })}
        />
      </div>
    </div>
  )
}

export default CreateSelect
