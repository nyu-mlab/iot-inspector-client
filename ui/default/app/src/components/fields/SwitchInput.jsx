import React from 'react'
import Label from './label'
import { Switch } from '@headlessui/react'
// import Hint from './hint'

const SwitchInput = ({
    className, hint, type, label, field, onChange, toggle, active,
    form: {
        errors,
        touched,
    },
}) => {
    // deleting field.value, this throws an error with the Checkbox Element.
    delete field.value

    return (
        <div className={`form-group ${className}`}>
            <Label label={label} hint={hint} />
            <div className="d-flex align-items-center">

                <Switch
                    {...field}
                    checked={field.checked}
                    onChange={onChange}
                    className="relative inline-flex items-center h-6 transition-colors rounded-full bg-light w-11 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                >
                    <span
                        className={`${field.checked ? 'translate-x-6 bg-green-400' : 'translate-x-1 bg-gray-400/50'
                            } inline-block h-4 w-4 transform rounded-full  transition-transform`}
                    />
                </Switch>
                {/* {active && (
                    <div className={`status ${active ? 'active' : ''}`}>
                        {active ? 'Active' : 'Inactive'}
                    </div>
                )} */}
            </div>
        </div>
    )
}

export default SwitchInput