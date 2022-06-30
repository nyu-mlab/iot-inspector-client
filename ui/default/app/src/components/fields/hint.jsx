import React from 'react'
import PropTypes from 'prop-types'
// import { Popup } from 'semantic-ui-react'

const FieldHint = ({ content }) => {
  return (
    <div className="pt-1 ml-1 d-inline-block hint">
      {/* <Popup
        trigger={<i className="fas fa-question-circle icon"></i>}
        content={content}
        position="right center"
        inverted
        size="tiny"
      /> */}
    </div>
  )
}

FieldHint.propTypes = {
  content: PropTypes.string
}

export default FieldHint
