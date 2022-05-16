import React from 'react'
import DefaultLayout from "../layouts/DefaultLayout"

const Constent = () => {
  return (
    <DefaultLayout>
      <main className="flex mt-[80px] bg-gray-100 h-[calc(100vh-80px)] w-full">
        <div className="p-4 mx-auto bg-white shadow-md md:p-8 md:my-8 rounded-2xl">
          <div className="flex flex-col items-center justify-center h-full max-w-2xl gap-8 mx-auto text-center">
            <h1>Consent Statement</h1>
            <div className="h-48 overflow-scroll md:px-8">
              <p>
                Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, cons ectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
              </p>
              <p>
                Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, cons ectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam
              </p>
            </div>
            <button className="btn btn-primary">
              I hereby give my consent
            </button>
            <a className="text-dark/50" href="/">No, I do not give my consent</a>
          </div>
        </div>
      </main>
    </DefaultLayout>
  )
}

export default Constent