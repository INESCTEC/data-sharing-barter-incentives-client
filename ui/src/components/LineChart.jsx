import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// const data = [
//   { time: '2024-02-29T16:00:00.000Z', uv: 4000, pv: 2400, amt: 2400, tester: 2000},
//   { time: '2024-02-29T17:00:00.000Z', uv: 3000, pv: 1398, amt: 2210 },
//   { time: '2024-02-29T18:00:00.000Z', uv: 2000, pv: 9800, amt: 2290 },
//   { time: '2024-02-29T19:00:00.000Z', uv: 2780, pv: 3908, amt: 2000 },
//   { time: '2024-02-29T20:00:00.000Z', uv: 1890, pv: 4800, amt: 2181 },
//   { time: '2024-02-29T21:00:00.000Z', uv: 2390, pv: 3800, amt: 2500 },
//   { time: '2024-02-29T22:00:00.000Z', uv: 3490, pv: 4300, amt: 2100 },
// ];

const TimeSeriesLineChart = (data) => {
  console.log(data);
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart
        data={data.data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="datetime" />
        <YAxis label={{ value: 'Average Power (kW)', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TimeSeriesLineChart;
