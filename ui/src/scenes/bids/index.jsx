import {Box, Typography, useTheme} from "@mui/material";
import {DataGrid} from "@mui/x-data-grid";
import {tokens} from "../../theme";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import Header from "../../components/Header";
import {useEffect, useState} from "react";
import axios from "axios";
import CircularProgress from "@mui/material/CircularProgress";
import Link from '@mui/material/Link';

const Bids = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [sessions, setSessions] = useState(null);
  
  useEffect(() => {
    axios.get('http://localhost:8000/market/session')
      .then((response) => {
        if (response.status === 200 && response.data.data) {
          const sessions = response.data.data;
          const promises = sessions.map((session) => {
            return axios.get(`http://localhost:8000/market/session/bid/${session.session_number}`);
          });
          Promise.all(promises)
            .then((bidResponses) => {
              const lastBids = bidResponses.reduce((acc, bidResponse) => {
                return acc.concat(bidResponse.data.data);
              }, []);
              console.log(lastBids);
              setSessions(lastBids);
            })
            .catch((error) => {
              console.error("Error fetching bids:", error);
            });
        }
      })
      .catch((error) => {
        console.error("Error fetching sessions:", error);
      });
  }, []);
  
  
  const columns = [
    {
      field: "market_session",
      headerName: "Market Session",
      flex: 1,
    },
    {
      field: "resource",
      headerName: "Resource",
      flex: 1,
    },
    {
      field: "confirmed",
      headerName: "Confirmed",
      flex: 1,
    },
    {
      field: "registered_at",
      headerName: "Registered at",
      flex: 1,
    },
    {
      field: "max_payment",
      headerName: "Max Payment",
      flex: 1,
    },
    {
      field: "bid_price",
      headerName: "Bid price",
      flex: 1,
    },
    {
      field: "tangle_msg_id",
      headerName: "Tangle Message ID",
      flex: 1,
      renderCell: ({ row: { tangle_msg_id } }) => {
        return (
          <Box
            width="60%"
            m="0 auto"
            p="5px"
            display="flex"
            justifyContent="center"
            // backgroundColor={colors.greenAccent[600]}
            // borderRadius="4px"
          >
            <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
              <Link href={`https://explorer.iota.org/testnet/transaction/${tangle_msg_id}`}
                    color="primary"
                    underline="hover"
                    target="_blank"
              >
                {tangle_msg_id}
              </Link>
              <Link to={`/messages/${tangle_msg_id}`}></Link>
            </Typography>
          </Box>
        );
      },
    },
  ];
  
  return (
    <Box m="20px">
      <Header title="Bids" subtitle="List of the bids made to the market"/>
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
        {sessions && sessions.length >= 0 ? (
          <DataGrid checkboxSelection rows={sessions} columns={columns}/>
        ) : (
          <CircularProgress color="success" value={100}/>
        )}
      
      </Box>
    </Box>
  );
};

export default Bids;
