import React from "react"
import CurrentWeather from "./CurrentWeather"
import PersonDetails from "./PersonDetails"
import HTTPSig from "./HTTPSig"

function App() {
  return (
    <div className="app">
      <CurrentWeather />
      <HTTPSig />
      {/*<PersonDetails />*/}
    </div>
  )
}

export default App
