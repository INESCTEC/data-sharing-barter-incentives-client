import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SimpleBarChart = (data) => {
  // "data": [
  //   {
  //     "market_session": 1,
  //     "user": "9418ffec-bc29-47aa-a000-46b66e510c06",
  //     "resource": "e908de01-42cc-4b34-b250-bdf4fcb0c93c",
  //     "session_deposit": 16000000.0,
  //     "session_balance": 16000000.0,
  //     "session_payment": 0.0,
  //     "session_revenue": 0.0,
  //     "registered_at": "2024-03-03T16:19:13.152085Z"
  //   }
  // ]
  
  // const data = [
  //   { name: 'Page A', uv: 4000, pv: 2400, amt: 2400 },
  //   { name: 'Page B', uv: 3000, pv: 1398, amt: 2210 },
  //   { name: 'Page C', uv: 2000, pv: 9800, amt: 2290 },
  //   { name: 'Page D', uv: 2780, pv: 3908, amt: 2000 },
  //   { name: 'Page E', uv: 1890, pv: 4800, amt: 2181 },
  //   { name: 'Page F', uv: 2390, pv: 3800, amt: 2500 },
  //   { name: 'Page G', uv: 3490, pv: 4300, amt: 2100 },
  // ];
  
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        data={data.data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="market_session" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="session_deposit" fill="#90d6ff" />
        <Bar dataKey="session_payment" fill="#EE4B2B" />
        <Bar dataKey="session_revenue" fill="#85BB65" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SimpleBarChart;
