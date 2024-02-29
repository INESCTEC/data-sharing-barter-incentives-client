import {Box, Button, IconButton, Typography, useTheme} from "@mui/material";
import {tokens} from "../../theme";
import {mockTransactions} from "../../data/mockData";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import SavingsIcon from '@mui/icons-material/Savings';
import WindPowerIcon from '@mui/icons-material/WindPower';
import WalletIcon from "@mui/icons-material/Wallet";
// import PersonAddIcon from "@mui/icons-material/PersonAdd";
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentVeryDissatisfiedIcon from '@mui/icons-material/SentimentVeryDissatisfied';
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import BarChart from "../../components/BarChart";
import StatBox from "../../components/StatBox";
// import ProgressCircle from "../../components/ProgressCircle";
import {useEffect, useState} from "react";
import axios from "axios";
import numeral from 'numeral';
import CircularProgress from '@mui/material/CircularProgress';
import {mockData2} from "../../data/mockData2";

const Dashboard = () => {
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [resources, setResources] = useState(null);
  const [balance, setBalance] = useState(null);
  const [loadingResources, setLoadingResources] = useState(false);
  const [totalPayment, setTotalPayment] = useState(0);
  const [marketBalance, setMarketBalance] = useState(null);
  const [totalRevenue, setTotalRevenue] = useState(null);
  const [sessions, setSessions] = useState([]);
  
  // const getSessions = async () => {
  //   axios.get('http://localhost:8000/market/session').then((response) => {
  //     console.log(response);
  //     if (response.status === 200 && response.data.data) {
  //       // Sort the data by the 'open_ts' attribute
  //       const sortedSessions = response.data.data.sort((a, b) => {
  //         return new Date(b.staged_ts) - new Date(a.staged_ts);
  //       });
  //       setSessions(sortedSessions);
  //     }
  //   })
  // }
  
  const getMarketBalance = async () => {
    axios.get('http://localhost:8000/market/session/balance')
      .then((response) => {
        if (response.status === 200) {
          const data = response.data.data;
          console.log(data)
          setMarketBalance(data);
          const totalPayment = data.reduce((sum, item) => sum + item.session_payment, 0);
          const totalRevenue = data.reduce((sum, item) => sum + item.session_revenue, 0);
          setTotalPayment(totalPayment);
          setTotalRevenue(totalRevenue);
        }
      })
  }
  const getResources = async () => {
    setLoadingResources(true);
    axios.get('http://localhost:8000/user/resource').then((response) => {
      if (response.data.code === 200) {
        setResources(response.data.data.length);
      }
      setLoadingResources(false);
    })
  };
  
  const getBalance = async () => {
    axios.get('http://localhost:8000/wallet/balance?email=andre.f.garcia@inesctec.pt')
      .then((response) => {
        if (response.status === 200) {
          setBalance(response.data.baseCoin.available);
          // setBalance(response.data.data.balance);
        }
      })
  };
  
  useEffect(() => {
    // getSessions().then();
    getResources().then();
    getBalance().then();
    getMarketBalance().then();
    
    // const intervalId = setInterval(async () => {
    //   await getResources();
    //   await getBalance();
    // }, 60000); // Poll every 10 seconds
    
    // return () => clearInterval(intervalId); // Cleanup the interval on unmount
  }, []);
  
  
  return (
    <Box m="20px">
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        {/*<Header title="DASHBOARD"/>*/}
        <Header title="Dashboard" subtitle="Welcome to your dashboard"/>
        <Box>
          <Button
            sx={{
              backgroundColor: colors.blueAccent[700],
              color: colors.grey[100],
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            <SavingsIcon sx={{ mr: "10px" }}/>
            Fund wallet
          </Button>
        </Box>
      </Box>
      
      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {loadingResources ? (
            <CircularProgress color="success"/>
          ) : (
            <StatBox
              title={resources}
              subtitle="Resources"
              icon={
                <WindPowerIcon
                  sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
                />
              }
            />
          )}
        </Box>
        
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {totalRevenue ? (
            <StatBox
              title={numeral(totalRevenue).format('0,0')}
              subtitle="Total revenue (Shimmer)"
              icon={
                <SentimentSatisfiedAltIcon
                  sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
                />
              }
            />
          ) : (
            <CircularProgress color="success"/>
          )}
        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {totalPayment ? (
            <StatBox
              title={numeral(totalPayment).format('0,0')}
              subtitle="Total payment (Shimmer)"
              icon={
                <SentimentVeryDissatisfiedIcon
                  sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
                />
              }
            />
          ) : (
            <CircularProgress color="success"/>
          )}
        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {balance !== null ? (
            <StatBox
              title={numeral(balance).format('0,0')}
              subtitle="Wallet balance (Shimmer)"
              icon={
                <WalletIcon
                  sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
                />
              }
            />
          ) : (
            <CircularProgress color="success"/>
          )}
        
        </Box>
        {/* ROW 2 */}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Box
            mt="25px"
            p="0 30px"
            display="flex "
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography
                variant="h5"
                fontWeight="600"
                color={colors.grey[100]}
              >
                Forecasts received
              </Typography>
            
            </Box>
            <Box>
              <IconButton>
                <DownloadOutlinedIcon
                  sx={{ fontSize: "26px", color: colors.greenAccent[500] }}
                />
              </IconButton>
            </Box>
          </Box>
          <Box height="250px" m="-20px 0 0 0">
            <LineChart isDashboard={true}/>
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 5"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
              Recent Market Transactions
            </Typography>
          </Box>
          {mockTransactions.map((transaction, i) => (
            <Box
              key={`${transaction.txId}-${i}`}
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              borderBottom={`4px solid ${colors.primary[500]}`}
              p="15px"
            >
              <Box>
                <Typography
                  color={colors.greenAccent[500]}
                  variant="h5"
                  fontWeight="600"
                >
                  {transaction.txId}
                </Typography>
                <Typography color={colors.grey[100]}>
                  {transaction.user}
                </Typography>
              </Box>
              <Box color={colors.grey[100]}>{transaction.date}</Box>
              <Box
                backgroundColor={colors.greenAccent[500]}
                p="5px 10px"
                borderRadius="4px"
              >
                ${transaction.cost}
              </Box>
            </Box>
          ))}
        </Box>
        
        {/* ROW 3 */}
        {/*<Box*/}
        {/*  gridColumn="span 4"*/}
        {/*  gridRow="span 2"*/}
        {/*  backgroundColor={colors.primary[400]}*/}
        {/*  p="30px"*/}
        {/*>*/}
        {/*  <Typography variant="h5" fontWeight="600">*/}
        {/*    Campaign*/}
        {/*  </Typography>*/}
        {/*  <Box*/}
        {/*    display="flex"*/}
        {/*    flexDirection="column"*/}
        {/*    alignItems="center"*/}
        {/*    mt="25px"*/}
        {/*  >*/}
        {/*    <ProgressCircle size="125"/>*/}
        {/*    <Typography*/}
        {/*      variant="h5"*/}
        {/*      color={colors.greenAccent[500]}*/}
        {/*      sx={{ mt: "15px" }}*/}
        {/*    >*/}
        {/*      $48,352 revenue generated*/}
        {/*    </Typography>*/}
        {/*    <Typography>Includes extra misc expenditures and costs</Typography>*/}
        {/*  </Box>*/}
        {/*</Box>*/}
        
        <Box
          gridColumn="span 8"
          gridRow="span 3"
          backgroundColor={colors.primary[400]}
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ padding: "30px 30px 0 30px" }}
          >
            Session Balance by Resource
          </Typography>
          {marketBalance && marketBalance.length > 0 ? (
            <Box height="450px" mt="-20px">
              <BarChart isDashboard={true} data={marketBalance}/>
            </Box>
          ) : (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              gridColumn="span 8"
              gridRow="span 3"
            >
              <CircularProgress color="success"/>
            </Box>
          )}
        </Box>
      
      
      </Box>
    </Box>
  );
};

export default Dashboard;
