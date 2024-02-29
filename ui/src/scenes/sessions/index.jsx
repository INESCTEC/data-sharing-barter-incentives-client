import { Box } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import { mockDataContacts } from "../../data/mockData";
import Header from "../../components/Header";
import { useTheme } from "@mui/material";
import {useEffect, useState} from "react";
import axios from "axios";


const Sessions = (sessionsData) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [sessions, setSessions] = useState([]);
  
  useEffect(() => {
    axios.get('http://localhost:8000/market/session').then((response) => {
      console.log(response);
      if (response.status === 200 && response.data.data) {
        // Sort the data by the 'open_ts' attribute
        const sortedSessions = response.data.data.sort((a, b) => {
          return new Date(b.staged_ts) - new Date(a.staged_ts);
        });
        setSessions(sortedSessions);
      }
    })
  }, []);
  
  const columns = [
    // { field: "id", headerName: "ID", flex: 0.5 },
    { field: "session_number", headerName: "Session Number" },
    {
      field: "session_date",
      headerName: "Date",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "staged_ts",
      headerName: "Staged",
      // type: "number",
      // headerAlign: "left",
      // align: "left",
      flex: 1,
    },
    {
      field: "open_ts",
      headerName: "Open",
      flex: 1,
    },
    {
      field: "close_ts",
      headerName: "Closed",
      flex: 1,
    },
    {
      field: "finish_ts",
      headerName: "Finish",
      flex: 1,
    },
    {
      field: "status",
      headerName: "Status",
      flex: 1,
    },
    {
      field: "market_price",
      headerName: "Market price",
      flex: 1,
    },
    {
      field: "b_min",
      headerName: "B Min",
      flex: 1,
    },
    {
      field: "b_max",
      headerName: "B Max",
      flex: 1,
    },
    {
      field: "n_price_steps",
      headerName: "Price steps",
      flex: 1,
    },
    {
      field: "delta",
      headerName: "Delta",
      flex: 1,
    },
  ];

  return (
    <Box m="20px">
      <Header
        title="Sessions"
        subtitle="List of sessions"
      />
      <Box
        m="40px 0 0 0"
        height="75vh"
        sx={{
          "& .MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-cell": {
            borderBottom: "none",
          },
          "& .name-column--cell": {
            color: colors.greenAccent[300],
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.blueAccent[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.blueAccent[700],
          },
          "& .MuiCheckbox-root": {
            color: `${colors.greenAccent[200]} !important`,
          },
          "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
            color: `${colors.grey[100]} !important`,
          },
        }}
      >
        <DataGrid
          rows={sessions}
          columns={columns}
          components={{ Toolbar: GridToolbar }}
        />
      </Box>
    </Box>
  );
};

export default Sessions;
