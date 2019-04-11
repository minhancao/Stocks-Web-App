import React, { Component } from "react";
import "./App.css";
import { BrowserRouter } from "react-router-dom";
import { Route, Switch, Link } from "react-router-dom";
import CustomLayout from "./components/layout/CustomLayout";
import Dashboard from "./components/dashboard/Dashboard";
import Stockspage from "./components/stocks/Stockspage";
import Predictionspage from "./components/predictions/Predictionspage";

const DefaultContainer = () => (
  <div>
    <CustomLayout>
      <Route exact path="/" component={Dashboard} />
      <Route exact path="/stocks" component={Stockspage} />
      <Route exact path="/predictions" component={Predictionspage} />
    </CustomLayout>
  </div>
);

class App extends Component {
  render() {
    return (
      <div className="App">
        <BrowserRouter>
          <Switch>
            <Route component={DefaultContainer} />
          </Switch>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;
