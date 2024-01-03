/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*"],
  theme: {
    extend: {
      fontFamily: {
        body: ["Poppins"],
        montserrat: ["Montserrat"],
      },
      colors: {
        dominan: "#051B35",
        birucerah: "#007BFF",
        biru: "#6B66FF",
        birulagi: "#473BF0",
        pink: "#ED5AB3",
        mungkinpink: "#D9D9D9",
        kuningoranye: "#FFA732",
      },
    },
  },
  plugins: [],
};
