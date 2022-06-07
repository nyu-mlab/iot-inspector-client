import React from 'react'
import { useLocation } from 'react-router-dom';

/**
 * Gets query params
 * 
 * @useage
 *  http://localhost:3000/device-activity?deviceid=s5242
 *  let query = useQuery();
 *  query.get('deviceid')
 */
const useQueryParam = () => {
  const { search } = useLocation();
  return React.useMemo(() => new URLSearchParams(search), [search]);
}

export default useQueryParam