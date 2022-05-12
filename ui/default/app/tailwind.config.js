module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#00d17a",
        secondary: "#007bc7",
        dark: "#08103f",
        light: "#e5e5e5",
        gray: {
          100: '#F5F7F7'
        },
        green : {
          100: "#caf9e4",
          200: "#a2f1cf",
          300: "#79e9ba",
          400: "#51e1a4",
          500: "#28d98f",
          600: "#00d17a",
        },
        yellow : {
          100: "#f9dbb2",
          200: "#FAD29A",
          300: "#FBC981",
          400: "#FDC169",
          500: "#FEB850",
          600: "#FFAF38"
        },
        red : {
          100: "#F9B2C1",
          200: "#FA9CAE",
          300: "#FB859B",
          400: "#FD6F88",
          500: "#FE5875",
          600: "#FF4262",
        },
        blue : {
          100: "#CFEFFF",
          200: "#A6D8F4",
          300: "#7CC1E9",
          400: "#53A9DD",
          500: "#2992D2",
          600: "#007BC7",
        },
        purple : {
          100: "#F6D0FC",
          200: "#EAA6F3",
          300: "#DE7DEA",
          400: "#D253E0",
          500: "#C62AD7",
          600: "#BA00CE",
        },
        teal : {
          100: "#B4FCF5",
          200: "#99EDE6",
          300: "#7DDED6",
          400: "#62D0C7",
          500: "#46C1B7",
          600: "#2BB2A8",
        },
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
      }
    },
  },
  plugins: [],
}
