import React, { useMemo } from 'react'
import { dataUseage } from '../utils/utils'
import { format } from 'timeago.js'
import { useTable, useSortBy } from 'react-table'

const EndpointList = ({ data }) => {
  console.log(data)
  // TODO Data should be pulled in here to limit component refreshes....
  const tableData = useMemo(() => {
    return data.map((device) => {
      return {
        remoteParty: device.counterparty_hostname,
        country: device.name,
        device: device.device.device_info?.device_name || device.device.auto_name,
        dateUseage: dataUseage(device.outbound_byte_count),
        lastUpdated: format(
          new Date(device.last_updated_time_per_country * 1000),
          'en_US',
          'yyyy-MM-dd HH:mm:ss'
        ),
      }
    })
  }, [data])

  const columns = useMemo(
    () => [
      { Header: 'Remote Party', accessor: 'remoteParty' },
      { Header: 'Country', accessor: 'country' },
      { Header: 'Device', accessor: 'device' },
      { Header: 'Data Useage', accessor: 'dateUseage' },
      { Header: 'Last Updated', accessor: 'lastUpdated' },
    ],
    []
  )

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable(
      {
        columns,
        data: tableData,
      },
      useSortBy
    )

  return (
    <>
      <table
        {...getTableProps()}
        className="min-w-full my-4 overflow-hidden border-collapse divide-y divide-gray-300 rounded-t-lg"
      >
        <thead className=" bg-dark">
          {
            // Loop over the header rows
            headerGroups.map((headerGroup) => (
              // Apply the header row props
              <tr {...headerGroup.getHeaderGroupProps()}>
                {
                  // Loop over the headers in each row
                  headerGroup.headers.map((column) => (
                    // Apply the header cell props
                    <th
                      {...column.getHeaderProps(column.getSortByToggleProps())}
                      className="px-3 py-3.5 text-left text-sm font-semibold text-light"
                    >
                      {
                        // Render the header
                        column.render('Header')
                      }
                    </th>
                  ))
                }
              </tr>
            ))
          }
        </thead>
        {/* Apply the table body props */}
        <tbody {...getTableBodyProps()}>
          {
            // Loop over the table rows
            rows.map((row) => {
              // Prepare the row for display
              prepareRow(row)
              return (
                // Apply the row props
                <tr {...row.getRowProps()}>
                  {
                    // Loop over the rows cells
                    row.cells.map((cell) => {
                      // Apply the cell props
                      return (
                        <td {...cell.getCellProps()}>
                          {
                            // Render the cell contents
                            cell.render('Cell')
                          }
                        </td>
                      )
                    })
                  }
                </tr>
              )
            })
          }
        </tbody>
      </table>
    </>
  )
}

export default EndpointList
