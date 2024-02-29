import { useState } from "react";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import { Link } from "react-router-dom";
import "react-pro-sidebar/dist/css/styles.css";
import { tokens } from "../../theme";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import WindPowerIcon from '@mui/icons-material/WindPower';
import GitHubIcon from '@mui/icons-material/GitHub';
import ApiIcon from '@mui/icons-material/Api';
// import ContactsOutlinedIcon from "@mui/icons-material/ContactsOutlined";
import ReceiptOutlinedIcon from "@mui/icons-material/ReceiptOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
// import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
// import PieChartOutlineOutlinedIcon from "@mui/icons-material/PieChartOutlineOutlined";
// import TimelineOutlinedIcon from "@mui/icons-material/TimelineOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
// import MapOutlinedIcon from "@mui/icons-material/MapOutlined";
import PersonAddIcon from '@mui/icons-material/PersonAdd';

const Item = ({ title, to, icon, selected, setSelected }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <MenuItem
      active={selected === title}
      style={{
        color: colors.grey[100],
      }}
      onClick={() => setSelected(title)}
      icon={icon}
    >
      <Typography>{title}</Typography>
      <Link to={to} />
    </MenuItem>
  );
};

const Sidebar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selected, setSelected] = useState("Dashboard");

  return (
    <Box
      sx={{
        "& .pro-sidebar-inner": {
          background: `${colors.primary[400]} !important`,
        },
        "& .pro-icon-wrapper": {
          backgroundColor: "transparent !important",
        },
        "& .pro-inner-item": {
          padding: "5px 35px 5px 20px !important",
        },
        "& .pro-inner-item:hover": {
          color: "#868dfb !important",
        },
        "& .pro-menu-item.active": {
          color: "#6870fa !important",
        },
      }}
    >
      <ProSidebar collapsed={isCollapsed}>
        <Menu iconShape="square">
          {/* LOGO AND MENU ICON */}
          <MenuItem
            onClick={() => setIsCollapsed(!isCollapsed)}
            icon={isCollapsed ? <MenuOutlinedIcon /> : undefined}
            style={{
              margin: "10px 0 20px 0",
              color: colors.grey[100],
            }}
          >
            {!isCollapsed && (
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                ml="15px"
              >
                {/*<Typography variant="h3" color={colors.grey[100]}>*/}
                {/*  PREDICO CLIENT*/}
                {/*</Typography>*/}
                <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
                  <MenuOutlinedIcon />
                </IconButton>
              </Box>
            )}
          </MenuItem>

          {!isCollapsed && (
            <Box mb="25px">
              {/*<Box display="flex" justifyContent="center" alignItems="center">*/}
              {/*  <img*/}
              {/*    alt="profile-user"*/}
              {/*    width="100px"*/}
              {/*    height="100px"*/}
              {/*    src={`../../assets/user.png`}*/}
              {/*    style={{ cursor: "pointer", borderRadius: "50%" }}*/}
              {/*  />*/}
              {/*</Box>*/}
              <Box textAlign="center">
                <Typography
                  variant="h2"
                  color={colors.grey[100]}
                  fontWeight="bold"
                  sx={{ m: "10px 0 0 0" }}
                >
                  PREDICO
                </Typography>
                <Typography variant="h5" color={colors.greenAccent[500]}>
                  andre.f.garcia@inesctec.pt
                </Typography>
              </Box>
            </Box>
          )}

          <Box paddingLeft={isCollapsed ? undefined : "10%"}>
            <Item
              title="Dashboard"
              to="/"
              icon={<HomeOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />

            <Typography
              variant="h6"
              color={colors.grey[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Data
            </Typography>
            <Item
              title="Sessions"
              to="/sessions"
              icon={<PersonOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Resources"
              to="/resources"
              icon={<WindPowerIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Bids"
              to="/bids"
              icon={<ReceiptOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Typography
              variant="h6"
              color={colors.grey[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Account
            </Typography>
            <Item
              title="Add account"
              to="/form"
              icon={<PersonAddIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            {/*<Item*/}
            {/*  title="Calendar"*/}
            {/*  to="/calendar"*/}
            {/*  icon={<CalendarTodayOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}
            {/*<Item*/}
            {/*  title="FAQ Page"*/}
            {/*  to="/faq"*/}
            {/*  icon={<HelpOutlineOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}

            <Typography
              variant="h6"
              color={colors.grey[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Support
            </Typography>
            <Item
              title="FAQ Page"
              to="/faq"
              icon={<HelpOutlineOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Source code"
              to="https://www.github.com"
              icon={<GitHubIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="API Documentation"
              to="http://localhost:8000/docs"
              newTab={true}
              icon={<ApiIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            {/*<Item*/}
            {/*  title="Bar Chart"*/}
            {/*  to="/bar"*/}
            {/*  icon={<BarChartOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}
            {/*<Item*/}
            {/*  title="Pie Chart"*/}
            {/*  to="/pie"*/}
            {/*  icon={<PieChartOutlineOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}
            {/*<Item*/}
            {/*  title="Line Chart"*/}
            {/*  to="/line"*/}
            {/*  icon={<TimelineOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}
            {/*<Item*/}
            {/*  title="Geography Chart"*/}
            {/*  to="/geography"*/}
            {/*  icon={<MapOutlinedIcon />}*/}
            {/*  selected={selected}*/}
            {/*  setSelected={setSelected}*/}
            {/*/>*/}
          </Box>
        </Menu>
      </ProSidebar>
    </Box>
  );
};

export default Sidebar;
