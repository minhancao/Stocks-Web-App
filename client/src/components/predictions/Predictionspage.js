import React, { Component } from "react";
import {
  VictoryChart,
  VictoryAxis,
  VictoryTheme,
  VictoryLine,
  VictoryBrushContainer,
  createContainer
} from "victory";
import {
  Layout,
  Menu,
  Icon,
  Input,
  Button,
  Dropdown,
  DatePicker,
  Card,
  Row,
  Col,
  Statistic,
  Modal,
  Form,
  Radio
} from "antd";
import "antd/dist/antd.css";

import axios from "axios";

const { Header, Content, Sider, Footer } = Layout;

const sampleData = [
  { x: 1, y: 2 },
  { x: 2, y: 3 },
  { x: 3, y: 5 },
  { x: 4, y: 4 },
  { x: 5, y: 7 }
];

const VictoryZoomVoronoiContainer = createContainer("zoom", "voronoi");

const CollectionCreateForm = Form.create({ name: "form_in_modal" })(
  // eslint-disable-next-line
  class extends React.Component {
    render() {
      const { visible, onCancel, onCreate, form } = this.props;
      const { getFieldDecorator } = form;
      return (
        <Modal
          visible={visible}
          title="Add a new stock"
          okText="Add"
          onCancel={onCancel}
          onOk={onCreate}
        >
          <Form layout="vertical">
            <Form.Item label="Stock Symbol">
              {getFieldDecorator("Stock Symbol", {
                rules: [
                  {
                    required: true,
                    message: "Please input a stock symbol!"
                  }
                ]
              })(<Input />)}
            </Form.Item>
          </Form>
        </Modal>
      );
    }
  }
);

class Predictionspage extends Component {
  componentDidMount() {
    this.setState({
      chartWidth: window.innerWidth
    });
    window.addEventListener("resize", this.updateDimensions.bind(this));
  }
  componentWillUnmount() {
    window.removeEventListener("resize", this.updateDimensions, false);
  }
  constructor(props) {
    super(props);
    this.state = {
      stocks: {},
      display: "predictionmodel",
      zoomDomain: { x: [new Date(2017, 3, 20), new Date(2019, 3, 20)] },
      visible: false,
      stocksInfo: {},
      strokeColors: {},
      chartWidth: 0,
      modal1Visible: false
    }; //this is how you set up state
  }

  updateDimensions(event) {
    this.setState({
      chartWidth: event.target.innerWidth
    });
  }

  getRandomColor() {
    var letters = "0123456789ABCDEF";
    var color = "#";
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  setModal1Visible(modal1Visible) {
    this.setState({ modal1Visible });
  }

  showModal = () => {
    this.setState({ visible: true });
  };

  handleCancel = () => {
    this.setState({ visible: false });
  };

  handleCreate = () => {
    const form = this.formRef.props.form;
    form.validateFields((err, values) => {
      if (err) {
        return;
      }

      console.log("Received values of form: ", values);
      this.getStock(values["Stock Symbol"]);
      form.resetFields();
      this.setState({ visible: false });
    });
  };

  saveFormRef = formRef => {
    this.formRef = formRef;
  };

  getStock = stockID => {
    axios.get("/stocks/" + stockID).then(res => {
      var sigh = [];
      const hmm = JSON.parse(res.data);
      console.log(hmm.includes("Error"));
      if (hmm.includes("Error")) {
        this.setModal1Visible(true);
      } else {
        var index = 0;
        for (index = 0; index < hmm.length; index++) {
          sigh.push({
            x: new Date(hmm[index].x + "T12:00:00Z"),
            Open: hmm[index].Open,
            High: hmm[index].High,
            Close: hmm[index].Close,
            Low: hmm[index].Low,
            Volume: hmm[index].Volume
          });
        }
        var newStock = this.state.stocks;
        newStock[stockID] = sigh;
        var color = this.state.strokeColors;
        color[stockID] = this.getRandomColor();
        var newStock2 = this.state.stocksInfo;
        var date1 = new Date("2019-03-01" + "T12:00:00Z");
        var newStock3 = this.state.stocks[stockID].filter(
          item => +date1 === +item.x
        )[0];
        newStock2[stockID] = newStock3;
        this.setState({
          stocks: newStock,
          strokeColors: color,
          stocksInfo: newStock2
        });
        console.log(this.state.stocksInfo);
      }
    });
  };

  deleteStock = stockID => {
    var newStock = this.state.stocks;
    delete newStock[stockID];
    var color = this.state.strokeColors;
    delete color[stockID];
    this.setState({ stocks: newStock, strokeColors: color });
  };

  handleZoom(domain) {
    this.setState({ zoomDomain: domain });
  }

  addStock = value => {
    this.setState(prevState => ({
      stocks: [...prevState.stocks, { name: value }]
    }));
  };

  removeStock = name => {
    var array = [...this.state.stocks];
    var index = array.map(o => o.name).indexOf(name);
    if (index !== -1) {
      array.splice(index, 1);
      this.setState({ stocks: array });
    }
  };

  onDatePickerChange(date, dateString, stockID) {
    /*axios.get("/stockinfo/" + stockID + "/" + dateString).then(res => {
      const hmm = JSON.parse(res.data);
      var newStock = this.state.stocksInfo;
      newStock[stockID] = hmm;
      this.setState({ stocksInfo: newStock });
      console.log(this.state.stocksInfo);
    });*/
    var date1 = new Date(dateString + "T12:00:00Z");
    var newStock = this.state.stocksInfo;
    var newStock1 = this.state.stocks[stockID].filter(
      item => +date1 === +item.x
    )[0];
    if (newStock1 != null) {
      newStock[stockID] = newStock1;
      this.setState({ stocksInfo: newStock });
      console.log(this.state.stocksInfo);
    } else {
      newStock1 = {
        "No Stock Data": "No stock data was recorded for this date."
      };
      newStock[stockID] = newStock1;
      this.setState({ stocksInfo: newStock });
      console.log(this.state.stocksInfo);
      console.log("Date cannot be found");
    }
  }

  // Render the content
  renderChart = () => {
    // What page should show?
    switch (this.state.display) {
      case "predictionmodel":
        return (
          <div style={{ align: "left" }}>
            Prediction Model
          </div>
        ); //pass method to child

      case "linechart":
        return (
          <div>
            <VictoryChart
              width={this.state.chartWidth}
              height={750}
              scale={{ x: "time" }}
              domain={{ y: [0, 3000] }}
              containerComponent={
                <VictoryZoomVoronoiContainer
                  labels={d =>
                    `${d.x.toLocaleString("en-us", {
                      month: "long"
                    })} ${d.x.getDate()}, ${d.x.getFullYear()}, ${d.Close}`
                  }
                  zoomDimension="x"
                  zoomDomain={this.state.zoomDomain}
                  onZoomDomainChange={this.handleZoom.bind(this)}
                />
              }
            >
              <VictoryAxis crossAxis label="Time" />
              <VictoryAxis
                dependentAxis
                label="Price(USD)"
                domain={[0, 3000]}
                style={{ axisLabel: { padding: 35 } }}
              />
              {Object.keys(this.state.stocks).map(key => (
                <VictoryLine
                  key={key}
                  style={{
                    data: { stroke: this.state.strokeColors[key] }
                  }}
                  data={this.state.stocks[key]}
                  x="x"
                  y="Close"
                />
              ))}
            </VictoryChart>
            <VictoryChart
              padding={{ top: 0, left: 50, right: 50, bottom: 30 }}
              width={this.state.chartWidth}
              height={100}
              domain={{ y: [0, 3000] }}
              scale={{ x: "time" }}
              containerComponent={
                <VictoryBrushContainer
                  brushDimension="x"
                  brushDomain={this.state.zoomDomain}
                  onBrushDomainChange={this.handleZoom.bind(this)}
                />
              }
            >
              <VictoryAxis tickFormat={x => new Date(x).getFullYear()} />
              {Object.keys(this.state.stocks).map(key => (
                <VictoryLine
                  key={key}
                  style={{
                    data: { stroke: this.state.strokeColors[key] }
                  }}
                  data={this.state.stocks[key]}
                  x="x"
                  y="Close"
                />
              ))}
            </VictoryChart>
          </div>
        ); //pass method to child

      case "statistics":
        return (
          <div style={{ align: "left" }}>
            <Row gutter={16} style={{ paddingLeft: "20px", width: 1400 }}>
              {Object.keys(this.state.stocks).map(key => (
                <Col span={8}>
                  <Card
                    title={key}
                    extra={
                      <DatePicker
                        onChange={(date, dateString) =>
                          this.onDatePickerChange(undefined, dateString, key)
                        }
                        placeHolder="Select date to search"
                      />
                    }
                    style={{ height: 350 }}
                  >
                    {Object.keys(this.state.stocksInfo[key])
                      .filter(item1 => item1 !== "x")
                      .map(id => (
                        <Col span={12}>
                          <Statistic
                            title={id}
                            value={this.state.stocksInfo[key][id]}
                            precision={2}
                            valueStyle={{ color: "#3f8600" }}
                          />
                        </Col>
                      ))}
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        ); //pass method to child

      default:
        return (
          <VictoryChart theme={VictoryTheme.material}>
            <VictoryLine
              style={{
                data: { stroke: "#c43a31" },
                parent: { border: "1px solid #ccc" }
              }}
              data={sampleData}
            />
          </VictoryChart>
        );
    }
  };

  handleClick = (e) => {
    console.log('click ', e);
    console.log(e.key)
  }

  render() {
    return (
      <div className="App">
        <Modal
          title="Error"
          style={{}}
          visible={this.state.modal1Visible}
          onOk={() => this.setModal1Visible(false)}
          onCancel={() => this.setModal1Visible(false)}
        >
          <p>Error: Please input the correct stock symbol.</p>
        </Modal>
        <Layout style={{ height: "100vh" }}>
          <Sider width={200} style={{ background: "#fff" }}>
            <Menu
              theme="dark"
              mode="inline"
              onClick={this.handleClick}
              defaultSelectedKeys={["1"]}
              style={{ height: "100%", borderRight: 0, paddingTop: "10px" }}
            >
              <Button
                type="default"
                shape="round"
                size="large"
                onClick={this.showModal}
              >
                Add a stock{" "}
                <Icon
                  type="plus"
                  style={{
                    position: "relative",
                    left: "4px",
                    bottom: "3px",
                    color: "red"
                  }}
                />
              </Button>
              <CollectionCreateForm
                wrappedComponentRef={this.saveFormRef}
                visible={this.state.visible}
                onCancel={this.handleCancel}
                onCreate={this.handleCreate}
              />
              {Object.keys(this.state.stocks).map(key => (
                <Menu.Item align="left" key={key}>
                  <Button
                    size="small"
                    type="danger"
                    shape="circle"
                    onClick={() => this.deleteStock(key)}
                  >
                    <Icon
                      type="close"
                      style={{
                        position: "relative",
                        left: "2px",
                        bottom: "2px",
                        fontSize: "18px",
                        color: this.state.strokeColors[key]
                      }}
                    />
                  </Button>
                  {"  "}
                  {key}
                </Menu.Item>
              ))}
            </Menu>
          </Sider>
          <Layout>
            <Header style={{ padding: "0" }}>
              <Menu
                theme="dark"
                mode="horizontal"
                defaultSelectedKeys={["1"]}
                style={{ lineHeight: "64px" }}
                align="left"
              >
              <Menu.Item
                  key="predictionmodel"
                  onClick={() => this.setState({ display: "predictionmodel" })}
                >
                  <Icon
                    type="stock"
                    style={{ position: "relative", bottom: "4px" }}
                  />
                  Prediction Model
                </Menu.Item>
                <Menu.Item
                  key="linechart"
                  onClick={() => this.setState({ display: "linechart" })}
                >
                  <Icon
                    type="line-chart"
                    style={{ position: "relative", bottom: "4px" }}
                  />
                  Line Chart
                </Menu.Item>

                <Menu.Item
                  key="statistics"
                  onClick={() => this.setState({ display: "statistics" })}
                >
                  <Icon
                    type="file-text"
                    style={{ position: "relative", bottom: "4px" }}
                  />
                  Statistics
                </Menu.Item>
              </Menu>
            </Header>
            <Content
              style={{
                background: "#fff",
                padding: 0,
                margin: 0,
                minHeight: 280,
                textAlign: "left"
              }}
            >
              <div>{this.renderChart()}</div>
            </Content>
          </Layout>
        </Layout>
      </div>
    );
  }
}

export default Predictionspage;
