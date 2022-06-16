import React from 'react'

const Consent = () => {
  return (
    <>
      <main className="flex w-full h-full bg-gray-100">
        <div className="p-4 mx-auto bg-white shadow-md md:p-8 md:my-8 rounded-2xl h-fit">
          <div className="flex flex-col items-center justify-center max-w-2xl gap-8 mx-auto text-center h-fit">
            <h1>Consent Statement</h1>
            <div className="overflow-scroll h-72 md:px-8 ">
              <p>
                Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, cons ectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
              </p>
              <p>
                Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, cons ectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam
              </p>
            </div>
            <hr className="w-full md:w-9/12" />
            <form className="flex items-center gap-2 ">
              <input type="checkbox" id="ScanDevices" checked/>
              <label htmlFor="ScanDevices" className="text-dark/50 h4">Scan for devices on my network</label>
            </form>
            <a className="btn btn-primary" href="/">
              I hereby give my consent
            </a>
            <a className="text-dark/50 h4" href="/">No, I do not give my consent</a>
          </div>
        </div>
      </main>
    </>
  )
}

export default Consent