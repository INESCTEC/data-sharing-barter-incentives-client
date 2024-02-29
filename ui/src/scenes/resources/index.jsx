import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import { mockDataInvoices } from "../../data/mockData";
import Header from "../../components/Header";
import {useEffect, useState} from "react";
import axios from "axios";

const Resources = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [resources, setResources] = useState([])
  
  useEffect(() => {
    axios.get('http://localhost:8000/user/resource').then((response) => {
      console.log(response);
      if (response.status === 200 && response.data.data) {
        // Sort the data by the 'registered_at' attribute
        
        setResources(response.data.data);
      }
    })
  }, []);
  
  const columns = [
    { field: "id", headerName: "ID" },
    {
      field: "name",
      headerName: "Name",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "type",
      headerName: "Type",
      flex: 1,
    },
    {
      field: "to_forecast",
      headerName: "To Forecast",
      flex: 1,
    },
    {
      field: "registered_at",
      headerName: "Registered at",
      flex: 1,
    },
    {
      field: "user",
      headerName: "User",
      flex: 1,
    },
  ];

  return (
    <Box m="20px">
      <Header title="Resources" subtitle="List of active resources" />
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
        }}
      >
        <DataGrid checkboxSelection rows={resources} columns={columns} />
      </Box>
    </Box>
  );
};

export default Resources;
