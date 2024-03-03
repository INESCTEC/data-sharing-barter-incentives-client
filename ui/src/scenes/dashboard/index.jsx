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
import moment from "moment";


const Dashboard = () => {
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [email, setEmail] = useState('andre.f.garcia@inesctec.pt');
  const [requestFundloading, setRequestFundLoading] = useState(false);
  const [resources, setResources] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loadingResources, setLoadingResources] = useState(false);
  const [totalPayment, setTotalPayment] = useState(null);
  const [marketBalance, setMarketBalance] = useState(null);
  const [totalRevenue, setTotalRevenue] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [measurements, setMeasurements] = useState(null);
  
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
  
  const getMeasurements = async () => {
    // const daysPast = 4;
    // const pastDate = moment().subtract(daysPast, 'days').utc().format('YYYY-MM-DDTHH:mm:ss[Z]');
    // const futureDate = moment().add(daysPast, 'days').utc().format('YYYY-MM-DDTHH:mm:ss[Z]');
    //
    // console.log(pastDate, futureDate);
    // resources.forEach(resource => {
    //   let url = `http://localhost:8000/data/raw-data/${pastDate}/${futureDate}/${resource.id}`;
    //   console.log(url);
    //   axios.get(url).then((response) => {
    //     setMeasurements(response.data.data);
    //     console.log()
    //   })
    // });
    
  }
  const fundWallet = async () => {
    setRequestFundLoading(true);
    axios.get("http://localhost:8000/wallet/request_funds?email=${email}/")
      .then((response) => {
        if (response.status === 200) {
          setRequestFundLoading(false);
        }
      })
      .catch((error) => {
        console.error("Error requesting funds:", error);
        setRequestFundLoading(false);
      });
  }
  const getTransactions = async () => {
    axios.get('http://localhost:8000/market/session/transactions').then((response) => {
      if (response.status === 200 && response.data.data) {
        const transactions = response.data.data;
        // order transactions
        transactions.sort((a, b) => {
          return new Date(b.registered_at) - new Date(a.registered_at);
        });
        setTransactions(transactions);
      }
      
      
    })
  };
  const getForecast = async () => {
    const today = moment(); // Use moment() to get the current date
    const weekAgo = moment(today).subtract(7, 'days');
    
    // Format dates to ISO 8601 format
    const todayFormatted = today.format('YYYY-MM-DDTHH:mm:ss[Z]');
    const weekAgoFormatted = weekAgo.format('YYYY-MM-DDTHH:mm:ss[Z]');
    console.log(todayFormatted, weekAgoFormatted);
    
    try {
      const resourcesResponse = await axios.get('http://localhost:8000/user/resource');
      
      if (resourcesResponse.status === 200) {
        const resources = resourcesResponse.data.data;
        
        // Array to store all forecast promises
        const forecastPromises = [];
        
        for (const resource of resources) {
          const url = `http://localhost:8000/data/forecast/${weekAgoFormatted}/${todayFormatted}/${resource.id}`;
          
          // Push the promise to the array
          forecastPromises.push(
            axios.get(url)
              .then((forecastResponse) => {
                if (forecastResponse.status === 200 && forecastResponse.data.data) {
                  const forecastData = {};
                  
                  // Group forecast data by resource_name
                  forecastResponse.data.data.forEach(item => {
                    const resourceName = item.resource_name;
                    const formattedDate = moment(item.datetime).toISOString();
                    
                    if (!forecastData[resourceName]) {
                      forecastData[resourceName] = [];
                    }
                    
                    forecastData[resourceName].push({
                      x: formattedDate,
                      y: item.value
                    });
                  });
                  setForecast(forecastData);
                  // Return the final forecast data
                  // console.log(forecastData);
                  // return Object.keys(forecastData).map(resourceName => ({
                  //   id: resourceName,
                  //   data: forecastData[resourceName]
                  // }));
                } else {
                  console.error("Error fetching forecast data:", forecastResponse.data);
                  return []; // Return an empty array if data is not available
                }
              })
              .catch((error) => {
                console.error("Error fetching forecast:", error);
                return []; // Return an empty array if there's an error
              })
          );
        }
        
        // Wait for all forecast promises to resolve
        const allForecasts = await Promise.all(forecastPromises);
        
        // Flatten the array of forecasts
        const finalForecast = allForecasts.flat();
        setForecast(finalForecast);
      }
    } catch (error) {
      console.error("Error fetching resources:", error);
    }
  }
  
  
  const getMarketBalance = async () => {
    axios.get('http://localhost:8000/market/session/balance')
      .then((response) => {
        if (response.status === 200) {
          const data = response.data.data;
          if (data) {
            const totalPayment = data.reduce((sum, item) => sum + item.session_payment, 0);
            const totalRevenue = data.reduce((sum, item) => sum + item.session_revenue, 0);
            data.forEach(item => {
              item.session_payment = item.session_payment / 1000000;
              item.session_revenue = item.session_revenue / 1000000;
              item.session_deposit = item.session_deposit / 1000000;
              item.session_balance = item.session_balance / 1000000;
            });
            
            setMarketBalance(data);
            setTotalPayment(totalPayment);
            setTotalRevenue(totalRevenue);
          } else {
            setTotalRevenue(0)
            setTotalPayment(0)
            setMarketBalance([]);
            console.error("Data is null or undefined.");
          }
        }
        // setTotalRevenue(0)
        // setTotalPayment(0)
        // setMarketBalance([]);
      })
      .catch((error) => {
        console.error("Error fetching market balance:", error);
      });
  }
  const getResources = async () => {
    setLoadingResources(true);
    axios.get('http://localhost:8000/user/resource').then((response) => {
      if (response.data.code === 200) {
        setResources(response.data.data);
        const daysPast = 4;
        const pastDate = moment().subtract(daysPast, 'days').utc().format('YYYY-MM-DDTHH:mm:ss[Z]');
        const futureDate = moment().add(daysPast, 'days').utc().format('YYYY-MM-DDTHH:mm:ss[Z]');
        
        response.data.data.forEach(resource => {
          let url = `http://localhost:8000/data/raw-data/${pastDate}/${futureDate}/${resource.id}`;
          console.log(url);
          axios.get(url).then((response) => {
            console.log(response);
            setMeasurements(response.data.data);
          })
        })
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
    console.log("entering get resources");
    getResources().then();
    console.log("entering set balance");
    getBalance().then();
    console.log("entering get market balance")
    getMarketBalance().then();
    getForecast().then();
    getTransactions().then();
    getMeasurements().then();
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
            onClick={fundWallet}
          >
            <SavingsIcon sx={{ mr: "10px" }}/>
            {requestFundloading ? 'Requesting...' : 'Fund wallet'}
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
              title={resources ? resources.length : 0}
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
          {totalRevenue === 0 || totalRevenue > 0 ? (
            <StatBox
              title={(totalRevenue / 1000000).toFixed(3)}
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
          {totalPayment === 0 || totalPayment > 0 ? (
            <StatBox
              title={(totalPayment / 1000000).toFixed(3)}
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
              title={(balance / 1000000).toFixed(3)}
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
          gridRow="span 3"
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
            { measurements ? ( <LineChart data={measurements}/>) : ''}
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 6"
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
          {transactions.map((transaction, i) => (
            <Box
              key={`${transaction.registered_at}`}
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
                  {transaction.resource_name}
                </Typography>
                <Typography color={colors.grey[100]}>
                  {transaction.transaction_type === 'transfer_in' ? 'Deposit to Market' :
                    transaction.transaction_type === 'payment' ? 'Payment to Market' :
                      transaction.transaction_type === 'revenue' ? 'Revenue' : 'Other'}
                </Typography>
              </Box>
              <Box color={colors.grey[100]}>{moment(transaction.registered_at).format("YYYY-MM-DD HH:mm:ss")}</Box>
              <Box
                backgroundColor={transaction.amount < 0 ? colors.redAccent[500] : colors.greenAccent[500]}
                p="5px 10px"
                borderRadius="4px"
              >
                {(transaction.amount / 1000000).toFixed(2)}
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
            Aggregated balance by session
          </Typography>
          
          <Box>
            <BarChart data={marketBalance}/>
          </Box>
        
        
        </Box>
      
      
      </Box>
    </Box>
  );
};

export default Dashboard;