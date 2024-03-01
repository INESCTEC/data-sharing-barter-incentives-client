import { useTheme } from "@mui/material";
import { ResponsiveBar } from "@nivo/bar";
import { tokens } from "../theme";
// import { mockBarData as data } from "../data/mockData";

const BarChart = ({ isDashboard = false , data}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const mergedData = data.reduce((acc, curr) => {
    const existingItemIndex = acc.findIndex(item => item.resource === curr.resource);
    if (existingItemIndex !== -1) {
      acc[existingItemIndex].session_deposit += curr.session_deposit;
      acc[existingItemIndex].session_balance += curr.session_balance;
      acc[existingItemIndex].session_payment += curr.session_payment;
      acc[existingItemIndex].session_revenue += curr.session_revenue;
    } else {
      acc.push({ ...curr }); // Ensure we're pushing a new object
    }
    return acc;
  }, []);
  // Extract unique market_session values
  // const marketSessions = [...new Set(data.map(item => item.market_session))];
  // const keys = marketSessions.map(session => `Session ${session}`);
  return (
    <ResponsiveBar
      data={mergedData}
      theme={{
        // added
        axis: {
          domain: {
            line: {
              stroke: colors.grey[100],
            },
          },
          legend: {
            text: {
              fill: colors.grey[100],
            },
          },
          ticks: {
            line: {
              stroke: colors.grey[100],
              strokeWidth: 1,
            },
            text: {
              fill: colors.grey[100],
            },
          },
        },
        legends: {
          text: {
            fill: colors.grey[100],
          },
        },
      }}

      keys={["session_deposit", "session_balance", "session_payment", "session_revenue"]}
      indexBy="resource"
      margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
      padding={0.3}
      valueScale={{ type: "linear" }}
      indexScale={{ type: "band", round: true }}
      colors={{ scheme: "nivo" }}
      defs={[
        {
          id: "dots",
          type: "patternDots",
          background: "inherit",
          color: "#38bcb2",
          size: 4,
          padding: 1,
          stagger: true,
        },
        {
          id: "lines",
          type: "patternLines",
          background: "inherit",
          color: "#eed312",
          rotation: -45,
          lineWidth: 6,
          spacing: 10,
        },
      ]}
      borderColor={{
        from: "color",
        modifiers: [["darker", "1.6"]],
      }}
      axisTop={null}
      axisRight={null}
      axisBottom={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "resources",
        legendPosition: "start",
        legendOffset: 15,
      }}
      axisLeft={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 40,
        legend: "Shimmer",
        legendPosition: "start",
        legendOffset: -40,
      }}
      enableLabel={false}
      labelSkipWidth={12}
      labelSkipHeight={12}
      labelTextColor={{
        from: "color",
        modifiers: [["darker", 1.6]],
      }}
      legends={[
        {
          dataFrom: "keys",
          anchor: "bottom-right",
          direction: "column",
          justify: false,
          translateX: 120,
          translateY: 0,
          itemsSpacing: 2,
          itemWidth: 115,
          itemHeight: 20,
          itemDirection: "left-to-right",
          itemOpacity: 0.85,
          symbolSize: 20,
          effects: [
            {
              on: "hover",
              style: {
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
      role="application"
      barAriaLabel={function (e) {
        return e.id + ": " + e.formattedValue + " in country: " + e.indexValue;
      }}
    />
  );
};

export default BarChart;
